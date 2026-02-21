from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re

def test_successful_login(page): #TC1 로그인 성공 테스트
    login_page = LoginPage(page)    
    login_page.login_to_system(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    expect(page).to_have_url(re.compile(".*#/dashboard"))

def test_failed_login(page): #TC2 로그인 실패 테스트
    login_page = LoginPage(page) 
    login_page.login_to_system(os.getenv("ADMIN_EMAIL"), "wrongpassword")
    expect(page.get_by_text("404")).to_be_visible(timeout=10000)

def test_api_login(page):# TC3 API로그인 테스트
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))      
    expect(page.get_by_text("DevFlow ERP")).to_be_visible(timeout=10000)


