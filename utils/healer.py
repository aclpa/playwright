"""
healer.py
---------
Playwright Locator 실패 시 YOLO + EasyOCR + NLP 의미 추론으로 자가 복구.

3개 엔진 모두 싱글톤:
  YOLOEngine  — utils/yolo.py
  NLPEngine   — utils/nlp.py
  OCREngine   — 이 파일 내부 (EasyOCR 래퍼)
"""

import time
import warnings
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

import cv2
import easyocr
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from utils.yolo import YOLOEngine
from utils.nlp import NLPEngine

warnings.filterwarnings("ignore", message=".*pin_memory.*")


# ──────────────────────────────────────────────────────────────────────────────
# OCREngine 싱글톤 — YOLO·NLP와 동일하게 1회만 로드
# ──────────────────────────────────────────────────────────────────────────────

class OCREngine:
    """EasyOCR 싱글톤 래퍼. 테스트 세션 내 1회만 로드합니다."""
    _instance: Optional["OCREngine"] = None

    def __init__(self, langs: list = None):
        _langs = langs or ["ko", "en"]
        print(f"⏳ OCREngine: EasyOCR 로딩 중... ({_langs})")
        self.reader = easyocr.Reader(_langs, gpu=False, verbose=False)
        print("✅ OCREngine: 로딩 완료")

    @classmethod
    def get_instance(cls, langs: list = None) -> "OCREngine":
        if cls._instance is None:
            cls._instance = cls(langs)
        return cls._instance

    def readtext(self, image, detail: int = 0) -> list:
        return self.reader.readtext(image, detail=detail)


# ──────────────────────────────────────────────────────────────────────────────
# HealingReport
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class HealingReport:
    original_locator: str
    target_text: str
    success: bool
    method: str = ""
    clicked_coords: Optional[tuple] = None
    suggested_locator: str = ""
    screenshot_path: str = ""
    debug_image_path: str = ""
    elapsed_ms: float = 0.0
    error_message: str = ""
    char_score: float = 0.0
    semantic_score: float = 0.0
    final_score: float = 0.0

    def log(self):
        border = "=" * 65
        status = "✅ 자가 복구 성공" if self.success else "❌ 자가 복구 실패"
        print(f"\n{border}")
        print(f"  🔧 AI 자가 복구 리포트")
        print(border)
        print(f"  상태           : {status}")
        print(f"  원본 Locator   : {self.original_locator}")
        print(f"  타겟 텍스트    : {self.target_text}")
        print(f"  복구 방법      : {self.target_text}")
        if self.clicked_coords:
            print(f"  클릭 좌표      : x={self.clicked_coords[0]}, y={self.clicked_coords[1]}")
        if self.final_score:
            print(f"  유사도         : 글자 {self.char_score:.2f}×0.4 "
                  f"+ 의미 {self.semantic_score:.2f}×0.6 = {self.final_score:.2f}")
        if self.suggested_locator:
            print(f"  추천 Locator   : {self.suggested_locator}")
        if self.screenshot_path:
            print(f"  스크린샷       : {self.screenshot_path}")
        if self.debug_image_path:
            print(f"  디버그 이미지  : {self.debug_image_path}")
        print(f"  소요 시간      : {self.elapsed_ms:.0f}ms")
        if self.error_message:
            print(f"  오류 메시지    : {self.error_message}")
        print(border + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# AIHealer
# ──────────────────────────────────────────────────────────────────────────────

class AIHealer:
    """
    Playwright TimeoutError 발생 시 YOLO+OCR+NLP로 자가 복구.
    3개 엔진 모두 싱글톤 공유 → 테스트 세션 내 각 1회만 로드.
    """

    CHAR_WEIGHT     = 0.4
    SEMANTIC_WEIGHT = 0.6

    CLASS_TO_ROLE = {
        0: "button", 1: "input", 2: "a",
        3: "avatar", 4: "select", 5: "icon-button", 8: "dialog-button",
    }

    def __init__(
        self,
        page: Page,
        model_path: str = "utils/best.pt",
        screenshot_dir: str = "testim/healing",
        ocr_lang: list = None,
        timeout: int = 5000,
        conf: float = 0.45,
    ):
        self.page = page
        self.timeout = timeout
        self.conf = conf
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # ── 3개 엔진 모두 싱글톤 — 중복 로드 없음 ────────────────────
        self.yolo = YOLOEngine.get_instance(model_path)
        self.nlp  = NLPEngine.get_instance()
        self.ocr  = OCREngine.get_instance(ocr_lang)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # utils/healer.py 의 중간 부분 교체

    def click(self, locator: str, target_text: str, timeout: int = None) -> HealingReport:
        t0 = time.time()
        report = HealingReport(original_locator=locator, target_text=target_text, success=False)

        try:
            self.page.locator(locator).click(timeout=timeout or self.timeout)
            report.success = True
            report.method  = "playwright_locator"
            report.elapsed_ms = (time.time() - t0) * 1000
            return report
        except PlaywrightTimeoutError:
            print(f"\n⚠️  Locator 실패: '{locator}' → AI 복구 시작 ('{target_text}')")
        except Exception as e:
            report.error_message = str(e)
            report.elapsed_ms = (time.time() - t0) * 1000
            report.log()
            raise

        ts         = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shot_path  = self.screenshot_dir / f"healing_{ts}.png"
        debug_path = self.screenshot_dir / f"healing_{ts}_debug.png"
        self.page.screenshot(path=str(shot_path))
        report.screenshot_path = str(shot_path)

        # ✨ 수정: 순수하게 4개의 결과값만 받음
        coords, suggested, debug_img, scores = self._find_target(str(shot_path), target_text)

        if debug_img is not None:
            cv2.imwrite(str(debug_path), debug_img)
            report.debug_image_path = str(debug_path)

        if scores:
            report.char_score     = scores.get("char", 0.0)
            report.semantic_score = scores.get("semantic", 0.0)
            report.final_score    = scores.get("final", 0.0)

        if coords:
            self.page.mouse.click(*coords)
            success = self._verify_click_result()
            report.success           = success
            report.method            = "yolo+ocr+nlp"
            report.clicked_coords    = coords
            report.suggested_locator = suggested
            # ✨ 피드백(오답 저장) 로직 완전 삭제됨
        else:
            report.method        = "failed"
            report.error_message = f"'{target_text}'를 화면에서 찾지 못했습니다."

        report.elapsed_ms = (time.time() - t0) * 1000
        report.log()

        if not report.success:
            raise RuntimeError(f"[AIHealer] 복구 실패: '{target_text}'")

        return report

    def fill(self, locator: str, target_text: str, value: str, timeout: int = None) -> HealingReport:
        t0 = time.time()
        report = HealingReport(original_locator=locator, target_text=target_text, success=False)

        try:
            self.page.locator(locator).fill(value, timeout=timeout or self.timeout)
            report.success = True
            report.method  = "playwright_locator"
            report.elapsed_ms = (time.time() - t0) * 1000
            return report
        except PlaywrightTimeoutError:
            print(f"\n⚠️  Locator 실패 (fill): '{locator}' → AI 복구 시작")

        ts         = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shot_path  = self.screenshot_dir / f"healing_fill_{ts}.png"
        debug_path = self.screenshot_dir / f"healing_fill_{ts}_debug.png"
        self.page.screenshot(path=str(shot_path))
        report.screenshot_path = str(shot_path)

        # ✨ 수정: 순수하게 4개의 결과값만 받음
        coords, suggested, debug_img, scores = self._find_target(
            str(shot_path), target_text, preferred_class=1
        )

        if debug_img is not None:
            cv2.imwrite(str(debug_path), debug_img)
            report.debug_image_path = str(debug_path)

        if scores:
            report.char_score     = scores.get("char", 0.0)
            report.semantic_score = scores.get("semantic", 0.0)
            report.final_score    = scores.get("final", 0.0)

        if coords:
            self.page.mouse.click(*coords)
            self.page.keyboard.type(value)
            report.success           = True
            report.method            = "yolo+ocr+nlp"
            report.clicked_coords    = coords
            report.suggested_locator = suggested
            # ✨ 피드백(오답 저장) 로직 완전 삭제됨
        else:
            report.method        = "failed"
            report.error_message = f"'{target_text}' 입력 필드를 찾지 못했습니다."

        report.elapsed_ms = (time.time() - t0) * 1000
        report.log()

        if not report.success:
            raise RuntimeError(f"[AIHealer] fill 복구 실패: '{target_text}'")

        return report

    def _find_target(self, image_path: str, target_text: str, preferred_class: int = None):
        image = cv2.imread(image_path)
        if image is None:
            return None, "", None, {} # ✨ 4개만 반환

        debug_img  = image.copy()
        detections = self.yolo.detect(image_path, conf=self.conf)

        if preferred_class is not None:
            detections = [d for d in detections if d["class_id"] == preferred_class]

        candidates = []
        # ✨ all_ocr_texts 수집 변수 삭제

        for det in detections:
            x1, y1, x2, y2 = det["box"]
            cx, cy   = det["center"]
            class_id = det["class_id"]

            ocr_results = self.ocr.readtext(det["crop"], detail=0)
            ocr_text    = " ".join(ocr_results).strip()

            char_s     = self._char_similarity(target_text, ocr_text)
            semantic_s = self.nlp.semantic_score(target_text, ocr_text) if ocr_text else 0.0
            final_s    = char_s * self.CHAR_WEIGHT + semantic_s * self.SEMANTIC_WEIGHT

            candidates.append((final_s, char_s, semantic_s, cx, cy, class_id, ocr_text, det["box"]))

            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 165, 255), 1)
            cv2.putText(debug_img, f"{ocr_text[:10]}({final_s:.2f})",
                        (x1, max(y1-4, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,165,255), 1)

        if not candidates:
            return None, "", debug_img, {} # ✨ 4개만 반환

        candidates.sort(key=lambda c: c[0], reverse=True)
        final_s, char_s, semantic_s, cx, cy, class_id, ocr_text, (x1,y1,x2,y2) = candidates[0]

        if final_s < 0.5:
            print(f"    ⚠️  앙상블 점수 {final_s:.2f} — 임계값(0.5) 미달")
            return None, "", debug_img, {} # ✨ 4개만 반환

        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.circle(debug_img, (cx, cy), 6, (0, 255, 0), -1)
        cv2.putText(debug_img, f"TARGET:{ocr_text}[{final_s:.2f}]",
                    (x1, max(y1-10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

        print(f"    ✅ '{ocr_text}': 글자 {char_s:.2f}×0.4 + 의미 {semantic_s:.2f}×0.6 = {final_s:.2f}")

        suggested = self._suggest_locator(class_id, ocr_text, target_text)
        scores    = {"char": char_s, "semantic": semantic_s, "final": final_s}
        
        # ✨ 깔끔하게 4개만 반환
        return (cx, cy), suggested, debug_img, scores

    def _verify_click_result(self, wait_ms: int = 800) -> bool:
        self.page.wait_for_timeout(wait_ms)
        for sel in [".q-notification--negative", "[role='alert'].error"]:
            if self.page.locator(sel).count() > 0:
                return False
        return True

    @staticmethod
    def _char_similarity(a: str, b: str) -> float:
        a, b = a.strip().lower(), b.strip().lower()
        if not a or not b: return 0.0
        if a == b:         return 1.0
        if a in b or b in a:
            return min(len(a), len(b)) / max(len(a), len(b))
        sa, sb = set(a), set(b)
        common = len(sa & sb)
        return (2 * common) / (len(sa) + len(sb)) if (sa or sb) else 0.0

    def _suggest_locator(self, class_id: int, ocr_text: str, target_text: str) -> str:
        t = ocr_text or target_text
        mapping = {
            0: f'button:has-text("{t}")',
            1: f'label:has-text("{t}")',
            2: f'a:has-text("{t}")',
            3: '.q-avatar, button:has(.q-avatar)',
            4: f'[role="combobox"]:near(:text("{t}"))',
            5: f'button[aria-label="{t}"]',
            8: f'.q-dialog button:has-text("{t}")',
        }
        return mapping.get(class_id, f'[data-testid="{t}"]')