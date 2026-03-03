import os
from utils.healer import AIHealer


class BasePage:
    def __init__(self, page):
        self.page     = page
        self.base_url = os.getenv("BASE_URL")
        self.api_url  = os.getenv("API_URL")
        self.healer   = AIHealer(page, model_path="utils/best.onnx")

    def navigate(self, path: str = "", timeout: int = None):
        self.page.goto(f"{self.base_url}{path}", timeout=timeout)

    def click(self, locator: str, target_text: str, timeout: int = None):
        return self.healer.click(locator, target_text, timeout=timeout)

    def fill(self, locator: str, target_text: str, value: str, timeout: int = None):
        return self.healer.fill(locator, target_text, value, timeout=timeout)