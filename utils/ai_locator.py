# utils/ai_locator.py
import os
import cv2
import easyocr
from ultralytics import YOLO
from pathlib import Path

class AILocator:
    def __init__(self, model_path="runs/detect/train/weights/best.pt"):
        # 1. 모델 경로 검증 및 로드
        self.model_path = Path(model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ 모델 파일을 찾을 수 없습니다: {self.model_path}")
        
        print(f"⏳ YOLO 모델 로딩 중... ({self.model_path.name})")
        self.model = YOLO(str(self.model_path))
        
        # 2. EasyOCR 엔진 로드 (GPU 활성화)
        print("⏳ OCR 엔진 로딩 중 (GPU 활성화)...")
        self.reader = easyocr.Reader(['en', 'ko'], gpu=True)
        
        # 3. 클래스 매핑 (data.yaml 기준)
        self.class_map = {'button': 0, 'input': 1, 'link': 2}

    def click_by_text(self, page, target_text, target_class="button", conf=0.01):
        """YOLO로 객체를 찾고 OCR로 텍스트를 대조하여 클릭합니다."""
        
        # 1. 스크린샷 캡처 (절대 경로)
        screenshot_path = Path("inference_temp.png").resolve()
        page.screenshot(path=str(screenshot_path))
        
        save_dir = Path("runs/detect").resolve()
        
        # 2. YOLO 추론 (해당 화면에서 객체들 찾기)
        results = self.model.predict(
            source=str(screenshot_path),
            conf=conf,
            imgsz=640,
            save=True,
            project=str(save_dir),
            name="predict",
            exist_ok=True,
            verbose=False # OCR 로그에 집중하기 위해 YOLO 로그는 끕니다
        )
        
        target_id = self.class_map.get(target_class)
        if target_id is None:
            print(f"❌ 알 수 없는 타겟 클래스입니다: {target_class}")
            return False

        # 3. OpenCV로 원본 이미지 읽기 (크롭용)
        img = cv2.imread(str(screenshot_path))
        print(f"\n🔍 '{target_text}' 텍스트가 포함된 '{target_class}'를 찾는 중...")
        
        for box in results[0].boxes:
            if int(box.cls[0]) == target_id:
                # 박스 좌표 추출
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # 이미지 크롭 (잘라내기)
                cropped_img = img[y1:y2, x1:x2]
                
                # 노이즈(너무 작은 박스) 무시
                if cropped_img.shape[0] < 5 or cropped_img.shape[1] < 5:
                    continue

                # 4. OCR 텍스트 추출
                ocr_result = self.reader.readtext(cropped_img, detail=0)
                extracted_text = " ".join(ocr_result).upper().replace(" ", "")
                compare_text = target_text.upper().replace(" ", "")
                
                # 5. 텍스트 일치 확인 및 클릭
                if compare_text in extracted_text:
                    center_x = float(box.xywh[0][0])
                    center_y = float(box.xywh[0][1])
                    
                    print(f"✅ 빙고! '{extracted_text}' 발견. (확신도: {float(box.conf[0]):.2f}) -> 좌표 ({center_x:.1f}, {center_y:.1f}) 클릭!")
                    page.mouse.move(center_x, center_y)
                    page.mouse.down()
                    page.mouse.up()
                    return True
                    
        print(f"❌ 화면에서 '{target_text}'를 찾지 못했습니다.")
        return False