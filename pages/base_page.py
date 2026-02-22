import os

class BasePage:
    def __init__(self, page):
        self.page = page
        self.base_url = os.getenv("BASE_URL")
        self.api_url = os.getenv("API_URL")

        
    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")
        