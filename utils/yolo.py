from ultralytics import YOLO
from pathlib import Path
import warnings

class AIVerifier:
    def __init__(self, model_path="utils/best.pt"):
        # 모델 경로 검증 및 로드
        self.model_path = Path(model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ YOLO 모델 파일을 찾을 수 없습니다: {self.model_path}")
        
        print(f"⏳ YOLO 검증 엔진 로딩 중... ({self.model_path.name})")
        self.model = YOLO(str(self.model_path))
        
        # data.yaml 기준 클래스 매핑 (수집기와 동일한 규칙)
        self.class_map = {'button': 0, 'input': 1, 'link': 2, 'avatar': 3, 'q-select': 4}
        warnings.filterwarnings("ignore", message=".*pin_memory.*")

    def get_detected_classes(self, image_path: str, conf=0.5, save_path: str=None) -> list:
        """
        이미지에서 발견된 모든 객체의 클래스 ID를 중복 없이 리스트로 반환합니다.
        (예: 아바타와 드롭다운이 있으면 [3, 4] 반환)
        """
        results = self.model.predict(
            source=image_path,
            conf=conf,
            verbose=False # 터미널 로그 숨김 (테스트 결과만 깔끔하게 보기 위해)
        )
        if save_path:
            results[0].save(filename=save_path)
            print(f"📸 AI 박스 판독 결과 저장 완료: {save_path}")
            
        detected_classes = []
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            detected_classes.append(class_id)
            
        return list(set(detected_classes)) # 중복 제거 후 반환

    def verify_element_exists(self, image_path: str, target_class: str, conf=0.5) -> bool:
        """
        테스트 코드에서 사용하기 쉬운 검증 함수 (True / False 반환)
        예: ai.verify_element_exists("screenshot.png", "avatar")
        """
        target_id = self.class_map.get(target_class)
        if target_id is None:
            raise ValueError(f"❌ 알 수 없는 타겟 클래스입니다: {target_class}")
            
        detected_classes = self.get_detected_classes(image_path, conf)
        
        if target_id in detected_classes:
            print(f"✅ 시각적 검증 통과: 화면에 '{target_class}' 요소가 정상적으로 렌더링 되었습니다.")
            return True
        else:
            print(f"🚨 시각적 버그 감지: 화면에 '{target_class}' 요소가 보이지 않습니다!")
            return False