from pages.login_page import LoginPage
from playwright.sync_api import expect
from pages.dashboard_page import DashboardPage
import os
import re
import allure


@allure.feature("인증")
@allure.story("로그인 성공")
@allure.severity(allure.severity_level.CRITICAL)
def test_successful_login(page):  # TC1 로그인 성공 테스트
    with allure.step("로그인 페이지 접속"):
        login_page = LoginPage(page)
        login_page.navigate()
    with allure.step("이메일/비밀번호 입력 후 로그인"):
        login_page.login_to_system(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    with allure.step("대시보드 URL 확인"):
        expect(page).to_have_url(re.compile(r".*/#/dashboard$"))


@allure.feature("인증")
@allure.story("API 로그인")
@allure.severity(allure.severity_level.NORMAL)
def test_api_login(page):  # TC2 API 로그인 테스트
    with allure.step("API로 로그인 토큰 발급"):
        login_page = LoginPage(page)
        login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    with allure.step("대시보드 페이지 접속"):
        login_page.navigate("#/dashboard")
    with allure.step("대시보드 URL 확인"):
        expect(page).to_have_url(re.compile(r".*/#/dashboard$"))


@allure.feature("인증")
@allure.story("로그아웃")
@allure.severity(allure.severity_level.NORMAL)
def test_logout(page):  # TC3 로그아웃 테스트
    with allure.step("API로 로그인"):
        login_page = LoginPage(page)
        dashboard_page = DashboardPage(page)
        login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    with allure.step("대시보드 접속"):
        login_page.navigate("#/dashboard", timeout=600000)
    with allure.step("유저 메뉴 클릭"):
        dashboard_page.user_menu()
    with allure.step("로그아웃 클릭"):
        dashboard_page.logout()
    with allure.step("로그인 페이지로 이동 확인"):
        expect(page).to_have_url(re.compile(r".*/#/auth/login"))