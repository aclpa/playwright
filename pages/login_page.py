# pages/login_page.py
from .base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page, request_context=None):
        super().__init__(page, request_context)
        # Selectors 
        self.email_fld = "//input[@aria-label='이메일' or @type='email']"
        self.password_fld = "//input[@type='password' or @aria-label='비밀번호']"
        self.login_btn = "//button[@type='submit' and @style=('font-size: 20px;')]"

    def login_to_system(self, email, password):
        """기존 UI 로그인 액션 플로우"""
        self.navigate()
        self.do_fill(self.email_fld, email)
        self.do_fill(self.password_fld, password)
        self.do_click(self.login_btn)

    # API를 활용한 초고속 로그인 우회
    def api_login(self, email, password):

        # 1. BasePage의 do_api_login 메서드 호출
        self.do_api_login(email, password)

        # 2. 로그인 페이지를 거치지 않고 바로 대시보드로 이동
        self.navigate("#/dashboard")

