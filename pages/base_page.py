"""
base_page.py
------------
모든 Page 클래스의 베이스.

healer 내장 구조:
  self.click(locator, target_text)  → healer.click() 경유
  self.fill(locator, target_text, value) → healer.fill() 경유
  self.page.locator().click()       → 기존 방식 그대로도 동작 (하위 호환)

각 Page 클래스 수정 방법:
  기존: self.page.locator('button:has-text("저장")').click()
  변경: self.click('button:has-text("저장")', "저장")
"""

import os
from utils.healer import AIHealer


class BasePage:
    def __init__(self, page):
        self.page     = page
        self.base_url = os.getenv("BASE_URL")
        self.api_url  = os.getenv("API_URL")
        self.healer   = AIHealer(page)   # 모든 Page에 자동 탑재

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")

    # ------------------------------------------------------------------
    # healer 경유 래퍼 — 각 Page 클래스에서 self.click() 으로 호출
    # ------------------------------------------------------------------

    def click(self, locator: str, target_text: str, timeout: int = None):
        """
        Playwright click 시도 → 실패 시 YOLO+OCR+NLP 자가 복구.

        사용 예시:
            self.click('button:has-text("저장")', "저장")
            self.click('button:has-text("Create")', "Create")
        """
        return self.healer.click(locator, target_text, timeout=timeout)

    def fill(self, locator: str, target_text: str, value: str, timeout: int = None):
        """
        Playwright fill 시도 → 실패 시 YOLO+OCR+NLP 자가 복구.

        사용 예시:
            self.fill('label:has-text("Title *")', "Title", "새 이슈")
        """
        return self.healer.fill(locator, target_text, value, timeout=timeout)