"""
yolo.py
-------
YOLO 공용 엔진 모듈.

클래스 구조:
  YOLOEngine  : 싱글톤 — 모델을 프로세스 내 1회만 로드, healer.py에서 공유
  AIVerifier  : 기존 인터페이스 유지 래퍼 — legacy 테스트 코드 호환
"""

import warnings
from pathlib import Path
from typing import Optional

import cv2
from ultralytics import YOLO

warnings.filterwarnings("ignore", message=".*pin_memory.*")


# ──────────────────────────────────────────────────────────────────────────────
# YOLOEngine — 싱글톤 공용 엔진
# ──────────────────────────────────────────────────────────────────────────────

class YOLOEngine:
    """
    YOLO 모델을 싱글톤으로 관리.
    AIVerifier와 AIHealer(healer.py)가 같은 인스턴스를 공유합니다.
    """

    _instance: Optional["YOLOEngine"] = None

    CLASS_MAP = {
        0: "button",
        1: "input",
        2: "link",
        3: "avatar",
        4: "q-select",
        5: "icon-button",
        6: "modal",
        7: "toast",
        8: "dialog-button",
    }
    NAME_TO_ID = {v: k for k, v in CLASS_MAP.items()}

    def __init__(self, model_path: str = "utils/best.pt"):
        path = Path(model_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"❌ YOLO 모델을 찾을 수 없습니다: {path}")
        print(f"⏳ YOLOEngine: 모델 로딩 중... ({path.name})")
        self.model = YOLO(str(path))
        print("✅ YOLOEngine: 로딩 완료")

    @classmethod
    def get_instance(cls, model_path: str = "utils/best.pt") -> "YOLOEngine":
        """싱글톤 인스턴스 반환. 최초 1회만 모델을 로드합니다."""
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def detect(
        self,
        image_path: str,
        conf: float = 0.5,
        save_path: Optional[str] = None,
    ) -> list[dict]:
        """
        이미지에서 모든 객체를 탐지하여 구조화된 결과 반환.

        Returns: list of {class_id, class_name, conf, box, center, crop}
        """
        results = self.model.predict(source=image_path, conf=conf, verbose=False)

        if save_path:
            results[0].save(filename=save_path)
            print(f"📸 YOLO 결과 저장: {save_path}")

        image = cv2.imread(image_path)
        h, w  = image.shape[:2]
        detections = []

        for box in results[0].boxes:
            class_id   = int(box.cls[0])
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 <= x1 or y2 <= y1:
                continue

            detections.append({
                "class_id"  : class_id,
                "class_name": self.CLASS_MAP.get(class_id, f"class_{class_id}"),
                "conf"      : confidence,
                "box"       : (x1, y1, x2, y2),
                "center"    : ((x1 + x2) // 2, (y1 + y2) // 2),
                "crop"      : image[y1:y2, x1:x2].copy(),
            })

        return detections

    def get_detected_class_ids(self, image_path: str, conf: float = 0.5) -> set[int]:
        return {d["class_id"] for d in self.detect(image_path, conf)}


# ──────────────────────────────────────────────────────────────────────────────
# AIVerifier — 기존 인터페이스 유지 (하위 호환)
# ──────────────────────────────────────────────────────────────────────────────

class AIVerifier:
    """
    기존 테스트 코드와의 하위 호환성을 유지하는 래퍼.
    내부적으로 YOLOEngine 싱글톤을 사용합니다.

    기존 사용법 그대로 동작:
        ai = AIVerifier()
        classes = ai.get_detected_classes("shot.png", conf=0.5)
        exists  = ai.verify_element_exists("shot.png", "avatar")
    """

    CLASS_MAP = {
        'button': 0, 'input': 1, 'link': 2, 'avatar': 3, 'q-select': 4
    }

    def __init__(self, model_path: str = "utils/best.pt"):
        self.engine = YOLOEngine.get_instance(model_path)

    def get_detected_classes(
        self,
        image_path: str,
        conf: float = 0.5,
        save_path: Optional[str] = None,
    ) -> list[int]:
        """감지된 클래스 ID 리스트 반환 (중복 제거)."""
        detections = self.engine.detect(image_path, conf=conf, save_path=save_path)
        return list({d["class_id"] for d in detections})

    def verify_element_exists(
        self,
        image_path: str,
        target_class: str,
        conf: float = 0.5,
    ) -> bool:
        """특정 클래스가 화면에 존재하는지 True/False 반환."""
        target_id = self.CLASS_MAP.get(target_class)
        if target_id is None:
            raise ValueError(f"❌ 알 수 없는 클래스: {target_class}")

        detected = self.engine.get_detected_class_ids(image_path, conf)

        if target_id in detected:
            print(f"✅ 시각적 검증 통과: '{target_class}' 렌더링 확인")
            return True
        else:
            print(f"🚨 시각적 버그 감지: '{target_class}' 가 보이지 않습니다!")
            return False