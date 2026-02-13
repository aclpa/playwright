import os
from datetime import datetime
from playwright.sync_api import Page, TimeoutError

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "localhost:8080/" # 대상 시스템 URL
        size = page.viewport_size
        if size['width'] != 1280 or size['height'] != 720:
            raise RuntimeError(
                f"❌ 해상도 불일치: 현재 {size['width']}x{size['height']}. "
                f"AI 탐지 최적화를 위해 1280x720이 강제되어야 합니다."
            )

    def navigate(self, path: str = ""):
        """페이지 이동"""
        self.page.goto(f"{self.base_url}")
        
    def do_click(self, selector: str, timeout: int = 5000):
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            self.page.click(selector)
        except TimeoutError:
            # Task 2.1: 실패 시 학습 데이터 자동 수집
            self._capture_for_learning(selector)
            # Phase 3: AI 자가 치유 로직 호출부 (예정)
            raise Exception(f"Element not found: {selector}. AI 자가 치유 엔진 연동 필요.")
    
    def do_fill(self, selector: str, value: str, timeout: int = 5000):
        """공통 입력 메서드"""
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)
        self.page.fill(selector, value)

    def _capture_for_learning(self, selector: str):
        """AI 학습용 스크린샷 캡처 (Task 1.4/2.1 연관)"""
        save_path = "datasets/raw_screenshots"
        os.makedirs(save_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.page.screenshot(path=f"{save_path}/fail_{timestamp}.png")