from playwright.sync_api import Page
import os

class BasePage:
    def __init__(self, page: Page, request_context=None):
        self.page = page
        self.request = request_context
        self.base_url = os.getenv("BASE_URL", "https://erp-sut.vercel.app/")
        size = page.viewport_size
        if size['width'] != 1280 or size['height'] != 720:
            raise RuntimeError(
                f"❌ 해상도 불일치: 현재 {size['width']}x{size['height']}. "
                f"AI 탐지 최적화를 위해 1280x720이 강제되어야 합니다."
            )

    def navigate(self, path: str = ""):
        """페이지 이동"""
        self.page.goto(f"{self.base_url}{path}")
        
    def do_click(self, selector: str, timeout: int = 5000):
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)
        self.page.click(selector)

    def do_fill(self, selector: str, value: str, timeout: int = 5000):
        """공통 입력 메서드"""
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)
        self.page.fill(selector, value)