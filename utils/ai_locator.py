# utils/ai_locator.py
import os
from ultralytics import YOLO

class AILocator:
    def __init__(self, model_path="runs/detect/train/weights/best.pt"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ 모델 파일을 찾을 수 없습니다: {model_path}")
        
        self.model = YOLO(model_path)
        # 클래스 매핑 (0: button, 1: input, 2: link)
        self.class_map = {'button': 0, 'input': 1, 'link': 2}

    def click_element(self, page, target_class="button", index=0):
        # 1. 추론용 임시 스크린샷
        screenshot_path = "inference_temp.png"
        page.screenshot(path=screenshot_path)
        
        print(f"🔍 AI 분석 시작 (찾는 대상: {target_class})...")

        # 2. AI 예측 실행 (옵션 강화!)
        results = self.model.predict(
            source=screenshot_path,
            conf=0.1,               # 💡 기준을 25% -> 10%로 낮춤 (더 잘 찾음)
            save=True,              # 💡 이미지 저장 필수
            project="runs/detect",  # 💡 대분류 폴더 강제 지정
            name="predict",         # 💡 소분류 폴더 강제 지정
            exist_ok=True           # 💡 predict2, predict3 생성 방지 (하나에 계속 저장)
        )
        
        # 3. 결과 분석
        target_id = self.class_map.get(target_class)
        found_boxes = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                # 디버깅용 로그 출력
                print(f"   👉 감지됨: Class {cls_id} (확신: {conf*100:.1f}%)")
                
                if cls_id == target_id:
                    x, y, w, h = box.xywh[0].tolist()
                    found_boxes.append((x, y))

        # 4. 클릭 액션
        if not found_boxes:
            print(f"⚠️ 실패: 화면에서 '{target_class}'(ID: {target_id})를 찾지 못했습니다.")
            # 실패했더라도 runs/detect/predict 폴더는 생겨야 정상입니다.
            return False
            
        if index >= len(found_boxes):
            index = -1
            
        target_x, target_y = found_boxes[index]
        print(f"🤖 AI 발견! 좌표({target_x:.1f}, {target_y:.1f})를 클릭합니다.")
        
        page.mouse.move(target_x, target_y)
        page.mouse.down()
        page.mouse.up()
        
        # 임시 파일 삭제
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
        return True