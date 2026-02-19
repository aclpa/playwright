from pages.login_page import LoginPage
from playwright.sync_api import expect
import os

admin_email = os.getenv("ADMIN_EMAIL")
admin_pass = os.getenv("ADMIN_PASS")
def test_successful_login(page): #TC1 로그인 성공 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행 
    login_page.login_to_system(admin_email, admin_pass)
    # 3. 결과 검증
    assert "/dashboard" in page.url

def test_failed_login(page): #TC2 로그인 실패 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행 
    login_page.login_to_system(admin_email, "wrongpassword")
    # 3. 결과 검증
    wait_for_error = page.wait_for_selector("span.error-code strong", state="visible")
    assert wait_for_error is not None

def test_api_login(page):# TC3 API로그인 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행
    login_page.api_login(admin_email, admin_pass)
    # 3. 결과 검증
    expect(page.get_by_role("main").get_by_text("Dash board")).to_be_visible()


