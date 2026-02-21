from .base_page import BasePage

class LoginPage(BasePage):

    def login_to_system(self, email, password):
        """기존 UI 로그인 액션 플로우"""
        self.navigate()
        self.page.locator("input[type='email']").fill(email)
        self.page.locator("input[type='password']").fill(password)
        self.page.locator("button[type='submit']").click()


    def api_login(self, email, password):
        self.do_api_login(email, password)
        self.navigate("#/dashboard")

    

