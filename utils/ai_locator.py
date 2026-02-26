import cv2
import easyocr
from ultralytics import YOLO
from pathlib import Path
import warnings

class AILocator:
    def __init__(self, model_path="utils/best.pt"):
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
        self.class_map = {'button': 0, 'input': 1, 'link': 2, 'avatar': 3, 'q-select': 4}

        warnings.filterwarnings("ignore", message=".*pin_memory.*")

    def click_by_text(self, page, target_text, target_class="button", conf=0.8, exact_match=False):
        """YOLO로 객체를 찾고 OCR로 텍스트를 대조하여 클릭합니다."""
        
        # 1. 스크린샷 캡처 (절대 경로)
        screenshot_path = Path("runs/detect/predict/inference_temp.png").resolve() 
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
            verbose=False # yolo 로그
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

                x1_expanded = max(0, x1 - 70)
                
                # 이미지 크롭 (잘라내기)
                cropped_img = img[y1:y2, x1_expanded:x2]

                # --- 💡 추가: OCR 시력 교정 (이미지 전처리) ---
                # 1. 컬러를 흑백으로 변환 (글자와 배경의 대비를 극대화)
                gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                
                # 2. 이미지를 2배로 확대 (작은 글씨 뭉개짐 방지)
                enlarged_img = cv2.resize(gray_img, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
                
                _, thresh_img = cv2.threshold(enlarged_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                # 4. 💡 [핵심 무기 2] 여백 (Padding) 추가: 
                # EasyOCR은 글자가 이미지 끝에 닿아있으면 인식을 포기하는 병이 있습니다. 사방에 20픽셀씩 흰색 여백을 줍니다.
                padded_img = cv2.copyMakeBorder(thresh_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])

                # 노이즈 무시
                if padded_img.shape[0] < 20 or padded_img.shape[1] < 20:
                    continue

                # 5. OCR 텍스트 추출 (가장 완벽해진 padded_img 투입!)
                ocr_result = self.reader.readtext(padded_img, detail=0)
                extracted_text = " ".join(ocr_result).upper().replace(" ", "")
                
                # 5. 텍스트 일치 확인 및 클릭
                is_match = False
                if exact_match:
                    # 정확히 일치 모드: 글자가 토시 하나 안 틀리고 똑같아야 통과 ("로그인" == "AUTHENTIKSSO로로그인" -> False)
                    is_match = (target_text.upper().replace(" ", "") == extracted_text)
                else:
                    # 포함 모드: 글자가 포함되어 있기만 하면 통과 (기존 방식)
                    is_match = (target_text.upper().replace(" ", "") in extracted_text)
                
                if is_match:
                    center_x = float(box.xywh[0][0])
                    center_y = float(box.xywh[0][1])
                    
                    print(f"✅ 빙고! '{extracted_text}' 발견. (확신도: {float(box.conf[0]):.2f}) -> 클릭!")
                    page.mouse.move(center_x, center_y)
                    page.mouse.down()
                    page.mouse.up()
                    return True
                    
        print(f"❌ 화면에서 '{target_text}'를 찾지 못했습니다.")
        return False