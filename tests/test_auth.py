from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re

admin_email = os.getenv("ADMIN_EMAIL")
admin_pass = os.getenv("ADMIN_PASS")

def test_successful_login(page): #TC1 로그인 성공 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)    
    # 2. 동작 수행
    login_page.login_to_system(admin_email, admin_pass)
    # 3. 결과 검증
    expect(page).to_have_url(re.compile(".*#/dashboard"))

def test_failed_login(page): #TC2 로그인 실패 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행 
    login_page.login_to_system(admin_email, "wrongpassword")
    # 3. 결과 검증
    expect(page.get_by_text("404")).to_be_visible()

def test_api_login(page):# TC3 API로그인 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행
    login_page.api_login(admin_email, admin_pass)
    # 3. 결과 검증
    expect(page.get_by_role("main").get_by_text("Dash board")).to_be_visible()


