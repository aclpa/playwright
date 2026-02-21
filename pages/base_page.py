import os
from utils.api_client import get_auth_data
import json


class BasePage:
    def __init__(self, page):
        self.page = page
        self.base_url = os.getenv("BASE_URL")
    def navigate(self, path: str = ""):
        """페이지 이동"""
        self.page.goto(f"{self.base_url}{path}")
        
    def do_api_login(self, email, password):
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
