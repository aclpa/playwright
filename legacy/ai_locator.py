import os
import cv2
import easyocr
from ultralytics import YOLO
from pathlib import Path
import warnings
from utils.nlp import NLPEngine  # 🌟 새로 만든 NLP 뇌 임포트

class AILocator:
    def __init__(self, model_path="runs/detect/train/weights/best.pt"):
        # 1. YOLO 비전 모델 로드
        self.model_path = Path(model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ 모델 파일을 찾을 수 없습니다: {self.model_path}")
        print(f"⏳ YOLO 비전 엔진 로딩 중... ({self.model_path.name})")
        self.model = YOLO(str(self.model_path))

        # 2. EasyOCR 엔진 로드
        print("⏳ OCR 엔진 로딩 중 (GPU 활성화)...")
        self.reader = easyocr.Reader(['en', 'ko'], gpu=True)

        # 3. NLP 추론 엔진 로드 (뇌 장착!)
        self.nlp = NLPEngine()

        self.class_map = {'button': 0, 'input': 1, 'link': 2}
        warnings.filterwarnings("ignore", message=".*pin_memory.*")

    def click_by_semantic_text(self, page, target_text, target_class="button", conf=0.1):
        """
        YOLO로 객체를 찾고, OCR로 읽은 후보군을 NLP에 넘겨 가장 의미가 맞는 버튼을 클릭합니다.
        """
        screenshot_path = Path("testim/debug/inference_temp.png").resolve()
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path)) 

        target_id = self.class_map.get(target_class)
        if target_id is None:
            print(f"❌ 알 수 없는 타겟 클래스입니다: {target_class}")
            return False

        # 1. YOLO 추론 (화면에서 버튼/링크 다 찾기)
        results = self.model.predict(
            source=str(screenshot_path),
            conf=conf,
            imgsz=640,
            verbose=False 
        )

        img = cv2.imread(str(screenshot_path))
        print(f"\n🔍 '{target_text}'의 의미를 가진 '{target_class}' 후보들을 화면에서 수집 중...")

        candidates = [] # 🌟 [핵심] 바로 클릭하지 않고 후보들을 모아둘 바구니

        # 2. 후보군 수집 루프
        for box in results[0].boxes:
            if int(box.cls[0]) == target_id:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_img = img[y1:y2, x1:x2]

                if cropped_img.shape[0] < 5 or cropped_img.shape[1] < 5:
                    continue

                # OCR 텍스트 추출
                ocr_result = self.reader.readtext(cropped_img, detail=0)
                extracted_text = " ".join(ocr_result).strip()

                # 글씨가 읽힌 경우에만 리스트에 추가 (좌표와 함께)
                if extracted_text:
                    center_x = float(box.xywh[0][0])
                    center_y = float(box.xywh[0][1])
                    candidates.append({
                        "text": extracted_text,
                        "coords": (center_x, center_y)
                    })

        # 3. NLP 뇌에게 추론 의뢰 (Data Flywheel 수집 로직 포함)
        if not candidates:
            print(f"❌ 화면에서 '{target_class}' 요소를 하나도 찾지 못했습니다.")
            return False

        best_match = self.nlp.find_best_match(target_text, candidates, threshold=0.5)

        # 4. 결과에 따른 Playwright 실행
        if best_match:
            x, y = best_match["coords"]
            text = best_match["text"]
            print(f"🎯 최종 클릭 타겟 확정: '{text}' (좌표: {x:.1f}, {y:.1f})")
            
            # DOM을 무시하고 모니터 절대 좌표 타격!
            page.mouse.click(x, y)
            return True
        else:
            return False