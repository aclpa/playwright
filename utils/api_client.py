import requests
import os

API_URL = os.getenv("API_URL")

def get_auth_data(email: str, password: str) -> dict:
    """API로 로그인하여 토큰 딕셔너리(access, refresh 등)를 반환합니다."""
    res = requests.post(
        f"{API_URL}api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=60
    )
    res.raise_for_status() # 에러 발생 시 즉시 중단
    return res.json()

