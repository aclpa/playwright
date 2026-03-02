import os
from utils.healer import AIHealer


class BasePage:
    def __init__(self, page):
        self.page     = page
        self.base_url = os.getenv("BASE_URL")
        self.api_url  = os.getenv("API_URL")
        self.healer   = AIHealer(page) 

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")

    def click(self, role: str, target_text: str, timeout: int = None):
        return self.healer.click(role, target_text, timeout=timeout)

    def fill(self, role: str, target_text: str, value: str, timeout: int = None):
        return self.healer.fill(role, target_text, value, timeout=timeout)
        