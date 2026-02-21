import os
import json

class BasePage:
    def __init__(self, page):
        self.page = page
        self.base_url = os.getenv("BASE_URL")
        self.api_url = os.getenv("API_URL")
    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")
        
    def do_api_login(self, email, password):
        login_data = {"email": email,"password": password}
        login_response = self.page.request.post(f"{self.api_url}api/v1/auth/login", data=login_data, timeout=60000)

        auth_data = login_response.json()
        access_token = auth_data.get("access_token")
        refresh_token = auth_data.get("refresh_token")

        auth_headers = {"Authorization": f"Bearer {access_token}"}
        response = self.page.request.get(f"{self.api_url}api/v1/auth/me", headers=auth_headers,timeout=10000)
    
        user_data = response.json()
        self.page.add_init_script(f"""
            window.localStorage.setItem('access_token', '{access_token}');
            window.localStorage.setItem('refresh_token', '{refresh_token}');
            window.localStorage.setItem('user', '{json.dumps(user_data)}');
        """)