# pages/login_page.py
from .base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Selectors 
        self.email_fld = "//input[@aria-label='이메일' or @type='email']"
        self.password_fld = "//input[@type='password' or @aria-label='비밀번호']"
        self.login_btn = "//button[@type='submit' and @style=('font-size: 20px;')]"

    def login_to_system(self, email, password):
        """로그인 액션 플로우"""
        self.navigate("/login")
        self.do_fill(self.email_fld, email)
        self.do_fill(self.password_fld, password)
        self.do_click(self.login_btn)