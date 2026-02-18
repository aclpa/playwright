# utils/ai_locator.py 수정본
import os
from ultralytics import YOLO
from pathlib import Path

class AILocator:
    def __init__(self, model_path="runs/detect/train/weights/best.pt"):
        # 윈도우/맥 호환 경로 처리
        self.model_path = Path(model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ 모델 파일을 찾을 수 없습니다: {self.model_path}")
        
        self.model = YOLO(str(self.model_path))
        self.class_map = {'button': 0, 'input': 1, 'link': 2}

    def click_element(self, page, target_class="button", index=0):
        # 1. 스크린샷 저장 (절대 경로)
        screenshot_path = Path("inference_temp.png").resolve()
        page.screenshot(path=str(screenshot_path))
        
        # 2. 저장 위치 강제 지정 (프로젝트 루트의 runs/detect/predict)
        save_dir = Path("runs/detect").resolve()
        
        print(f"\n🔍 AI 분석 시작 (Target: {target_class})")

        # 3. AI 예측 실행
        results = self.model.predict(
            source=str(screenshot_path),
            conf=0.01,               # 확신도를 더 낮춤
            imgsz=640,               # 💡 분석 사이즈를 640으로 명시
            save=True,
            project=str(save_dir),
            name="predict",
            exist_ok=True,
            augment=True
        )
        
        # 4. 결과 분석 (터미널 로그 출력 추가)
        found_boxes = []
        for result in results:
            print(f"📸 결과 저장 완료: {result.save_dir}") # 어디 저장됐는지 출력!
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                print(f"   👉 발견: ID {cls_id} ({conf*100:.1f}%)")
                
                if cls_id == self.class_map.get(target_class):
                    x, y, w, h = box.xywh[0].tolist()
                    found_boxes.append((x, y))

        if not found_boxes:
            print(f"⚠️ '{target_class}'를 찾지 못했습니다.")
            return False
            
        target_x, target_y = found_boxes[index if index < len(found_boxes) else -1]
        print(f"🤖 클릭 좌표: ({target_x:.1f}, {target_y:.1f})")
        
        page.mouse.move(target_x, target_y)
        page.mouse.down()
        page.mouse.up()
        return True