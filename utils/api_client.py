# untils/api_client.py
import requests
import os

API_URL = os.getenv(
    "API_URL",
    "https://erp-backend-api-ww9v.onrender.com"
)

def get_api_token(email: str, password: str) -> str:
    res = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=60
    )
    res.raise_for_status()
