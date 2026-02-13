# tests/test_auth.py
import pytest
from pages.login_page import LoginPage

def test_successful_login(page):
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    
    # 2. 동작 수행 
    login_page.login_to_system("admin@devflow.com", "devpassword")
    
    # 3. 결과 검증 (Assertion)
    assert "/dashboard" in page.url