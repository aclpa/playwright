# pages/login_page.py
import json
from .base_page import BasePage
from utils.api_client import get_auth_data

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
    def api_login_and_bypass(self, email, password):
        """API 토큰을 발급받아 로컬 스토리지에 주입하고 대시보드로 직행합니다."""
        # 1. API로 토큰 가져오기
        auth_data = get_auth_data(email, password)
        
        # 2. 프론트엔드가 요구하는 user 객체 문자열 생성 (이메일, 이름 동적 적용)
        user_data = {
            "id": 1,
            "email": email,
            "username": email.split("@")[0],
            "is_active": True,
            "is_admin": True,
            "authentik_id": "auth-admin-001",
            "avatar_url": None,
            "full_name": None,
            "phone": None,
            "created_at": "2026-02-10T19:38:27.467941",
            "updated_at": "2026-02-10T22:36:43.692191"
        }
        
        # 3. 페이지 로딩 전 로컬 스토리지 세팅 예약
        self.page.add_init_script(f"""
            window.localStorage.setItem('access_token', '{auth_data.get("access_token")}');
            window.localStorage.setItem('refresh_token', '{auth_data.get("refresh_token")}');
            window.localStorage.setItem('user', '{json.dumps(user_data)}');
        """)

        # 4. 로그인 페이지를 거치지 않고 바로 대시보드로 이동
        self.navigate("#/dashboard")

