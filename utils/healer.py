"""
healer.py  (구 ai_locator.py 대체)
------------------------------------
Playwright Locator 실패 시 YOLO + EasyOCR + NLP 의미 추론으로 자가 복구.

구 ai_locator.py 대비 변경사항:
  1. YOLOEngine 싱글톤 사용 — YOLO 중복 로드 제거
  2. NLPEngine 싱글톤 사용 — NLP 중복 로드 제거
  3. 글자 유사도 × 0.4 + 의미 유사도 × 0.6 앙상블 적용
  4. 클릭 결과 → confirm_last_match() 피드백 → verified Triplet 생성
  5. HealingReport로 복구 결과 리포팅 및 추천 Locator 제안
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

from utils.yolo import YOLOEngine   # 싱글톤 YOLO
from utils.nlp import NLPEngine     # 싱글톤 NLP (구 ai_locator의 NLPEngine과 동일 경로)

warnings.filterwarnings("ignore", message=".*pin_memory.*")


# ──────────────────────────────────────────────────────────────────────────────
# 리포트 데이터 클래스
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class HealingReport:
    original_locator: str
    target_text: str
    success: bool
    method: str = ""                        # playwright_locator | yolo+ocr+nlp | failed
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
        print(f"  복구 방법      : {self.method}")
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
# 메인 클래스
# ──────────────────────────────────────────────────────────────────────────────

class AIHealer:
    """
    구 AILocator를 대체하는 자가 복구 클래스.

    기존 사용법 (ai_locator.py):
        locator = AILocator()
        locator.click_by_semantic_text(page, "저장", "button")

    새 사용법 (healer.py):
        healer = AIHealer(page)
        healer.click('button:has-text("저장")', target_text="저장")
    """

    # 앙상블 가중치
    CHAR_WEIGHT     = 0.4
    SEMANTIC_WEIGHT = 0.6

    # YOLO 클래스 ID → 추천 Locator 태그
    CLASS_TO_ROLE = {
        0: "button",
        1: "input",
        2: "a",
        3: "avatar",
        4: "select",
        5: "icon-button",
        8: "dialog-button",
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

        # ── 싱글톤 공유 — 중복 로드 없음 ──────────────────────────────
        self.yolo = YOLOEngine.get_instance(model_path)
        self.nlp  = NLPEngine.get_instance()

        langs = ocr_lang or ["ko", "en"]
        print(f"⏳ EasyOCR 로딩 중... ({langs})")
        self.ocr = easyocr.Reader(langs, gpu=False, verbose=False)
        print("✅ AIHealer 준비 완료\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def click(
        self,
        locator: str,
        target_text: str,
        timeout: int = None,
    ) -> HealingReport:
        """
        Playwright click 시도 → 실패 시 YOLO+OCR+NLP로 자가 복구.

        사용 예시:
            healer.click('button:has-text("New Project")', target_text="New Project")
            healer.click('button:has-text("저장")', target_text="저장")
        """
        t0 = time.time()
        report = HealingReport(
            original_locator=locator,
            target_text=target_text,
            success=False,
        )

        # ── Step 1: 정상 Playwright 클릭 ──────────────────────────────
        try:
            self.page.locator(locator).click(timeout=timeout or self.timeout)
            report.success = True
            report.method  = "playwright_locator"
            report.elapsed_ms = (time.time() - t0) * 1000
            return report

        except PlaywrightTimeoutError:
            print(f"\n⚠️  Locator 실패: '{locator}'")
            print(f"    → AI 자가 복구 시작... (타겟: '{target_text}')")

        except Exception as e:
            report.error_message = str(e)
            report.elapsed_ms = (time.time() - t0) * 1000
            report.log()
            raise

        # ── Step 2: 스크린샷 캡처 ─────────────────────────────────────
        ts         = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shot_path  = self.screenshot_dir / f"healing_{ts}.png"
        debug_path = self.screenshot_dir / f"healing_{ts}_debug.png"
        self.page.screenshot(path=str(shot_path))
        report.screenshot_path = str(shot_path)

        # ── Step 3: YOLO + OCR + NLP 앙상블 탐색 ─────────────────────
        coords, suggested, debug_img, scores = self._find_target(
            str(shot_path), target_text
        )

        if debug_img is not None:
            cv2.imwrite(str(debug_path), debug_img)
            report.debug_image_path = str(debug_path)

        if scores:
            report.char_score     = scores.get("char", 0.0)
            report.semantic_score = scores.get("semantic", 0.0)
            report.final_score    = scores.get("final", 0.0)

        # ── Step 4: 클릭 및 결과 피드백 ──────────────────────────────
        if coords:
            self.page.mouse.click(*coords)
            success = self._verify_click_result()

            report.success           = success
            report.method            = "yolo+ocr+nlp"
            report.clicked_coords    = coords
            report.suggested_locator = suggested

            # 클릭 결과 → NLP 피드백 → verified Triplet 생성
            self.nlp.confirm_last_match(target_text, was_correct=success)
        else:
            report.method        = "failed"
            report.error_message = f"'{target_text}'를 화면에서 찾지 못했습니다."

        report.elapsed_ms = (time.time() - t0) * 1000
        report.log()

        if not report.success:
            raise RuntimeError(
                f"[AIHealer] 자가 복구 실패: '{target_text}'를 찾지 못했습니다."
            )

        return report

    def fill(
        self,
        locator: str,
        target_text: str,
        value: str,
        timeout: int = None,
    ) -> HealingReport:
        """
        Playwright fill 시도 → 실패 시 YOLO+OCR+NLP로 자가 복구.

        사용 예시:
            healer.fill('label:has-text("Title *")', target_text="Title", value="새 이슈")
        """
        t0 = time.time()
        report = HealingReport(
            original_locator=locator,
            target_text=target_text,
            success=False,
        )

        try:
            self.page.locator(locator).fill(value, timeout=timeout or self.timeout)
            report.success = True
            report.method  = "playwright_locator"
            report.elapsed_ms = (time.time() - t0) * 1000
            return report

        except PlaywrightTimeoutError:
            print(f"\n⚠️  Locator 실패 (fill): '{locator}'")
            print(f"    → AI 자가 복구 시작... (타겟: '{target_text}')")

        ts         = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shot_path  = self.screenshot_dir / f"healing_fill_{ts}.png"
        debug_path = self.screenshot_dir / f"healing_fill_{ts}_debug.png"
        self.page.screenshot(path=str(shot_path))
        report.screenshot_path = str(shot_path)

        coords, suggested, debug_img, scores = self._find_target(
            str(shot_path), target_text, preferred_class=1  # input
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
            self.nlp.confirm_last_match(target_text, was_correct=True)
        else:
            report.method        = "failed"
            report.error_message = f"'{target_text}' 입력 필드를 찾지 못했습니다."

        report.elapsed_ms = (time.time() - t0) * 1000
        report.log()

        if not report.success:
            raise RuntimeError(
                f"[AIHealer] fill 복구 실패: '{target_text}' 입력 필드를 찾지 못했습니다."
            )

        return report

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _find_target(
        self,
        image_path: str,
        target_text: str,
        preferred_class: int = None,
    ) -> tuple:
        """
        YOLO → bounding box 추출
        EasyOCR → 텍스트 읽기
        앙상블 → 글자 × 0.4 + 의미 × 0.6
        """
        image = cv2.imread(image_path)
        if image is None:
            return None, "", None, {}

        debug_img  = image.copy()
        detections = self.yolo.detect(image_path, conf=self.conf)

        if preferred_class is not None:
            detections = [d for d in detections if d["class_id"] == preferred_class]

        candidates = []

        for det in detections:
            x1, y1, x2, y2 = det["box"]
            cx, cy   = det["center"]
            class_id = det["class_id"]

            # OCR
            ocr_results = self.ocr.readtext(det["crop"], detail=0)
            ocr_text    = " ".join(ocr_results).strip()

            # ── 앙상블 유사도 ─────────────────────────────────────────
            char_s     = self._char_similarity(target_text, ocr_text)
            semantic_s = self.nlp.semantic_score(target_text, ocr_text) if ocr_text else 0.0
            final_s    = char_s * self.CHAR_WEIGHT + semantic_s * self.SEMANTIC_WEIGHT

            candidates.append((final_s, char_s, semantic_s, cx, cy, class_id, ocr_text, det["box"]))

            # 디버그: 회색 박스
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (180, 180, 180), 1)
            cv2.putText(
                debug_img,
                f"{ocr_text[:10]}({final_s:.2f})",
                (x1, max(y1 - 4, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1,
            )

        if not candidates:
            return None, "", debug_img, {}

        candidates.sort(key=lambda c: c[0], reverse=True)
        final_s, char_s, semantic_s, cx, cy, class_id, ocr_text, (x1, y1, x2, y2) = candidates[0]

        if final_s < 0.3:
            print(f"    ⚠️  앙상블 점수 {final_s:.2f} — 임계값(0.3) 미달")
            return None, "", debug_img, {}

        # 디버그: 선택된 박스 강조
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(debug_img, (cx, cy), 6, (0, 0, 255), -1)
        cv2.putText(
            debug_img,
            f"TARGET:{ocr_text}[{final_s:.2f}]",
            (x1, max(y1 - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
        )

        print(f"    ✅ '{ocr_text}': 글자 {char_s:.2f}×0.4 + 의미 {semantic_s:.2f}×0.6 = {final_s:.2f}")

        suggested = self._suggest_locator(class_id, ocr_text, target_text)
        scores    = {"char": char_s, "semantic": semantic_s, "final": final_s}
        return (cx, cy), suggested, debug_img, scores

    def _verify_click_result(self, wait_ms: int = 800) -> bool:
        """클릭 후 에러 토스트/다이얼로그가 없으면 성공으로 간주."""
        self.page.wait_for_timeout(wait_ms)
        for sel in [".q-notification--negative", "[role='alert'].error"]:
            if self.page.locator(sel).count() > 0:
                return False
        return True

    @staticmethod
    def _char_similarity(a: str, b: str) -> float:
        """글자 기반 유사도 (0.0 ~ 1.0)."""
        a, b = a.strip().lower(), b.strip().lower()
        if not a or not b: return 0.0
        if a == b:         return 1.0
        if a in b or b in a:
            return min(len(a), len(b)) / max(len(a), len(b))
        sa, sb = set(a), set(b)
        common = len(sa & sb)
        return (2 * common) / (len(sa) + len(sb)) if (sa or sb) else 0.0

    def _suggest_locator(self, class_id: int, ocr_text: str, target_text: str) -> str:
        """감지 클래스 + OCR 텍스트로 Playwright Locator 추천."""
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