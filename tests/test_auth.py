from pages.login_page import LoginPage
from playwright.sync_api import expect
from pages.ai_page import aipage
from pages.dashboard_page import DashboardPage
import os
import time

def test_successful_login(page):#TC1 로그인 성공 테스트   
    login_page = LoginPage(page)
    ai_page = aipage(page) 
    try: 
        login_page.navigate()
        login_page.login_to_system(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        expect(page.get_by_text("Dash board").first).to_be_visible(timeout=3000)
    except AssertionError:
        page.context.clear_cookies()
        page.evaluate("window.localStorage.clear(); window.sessionStorage.clear();")
        login_page.navigate()
        ai_page.login_successful_ai(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        expect(page.get_by_text("Dash board").first).to_be_visible(timeout=3000)


def test_failed_login(page): #TC2 로그인 실패 테스트
    login_page = LoginPage(page)
    ai_page = aipage(page) 
    try: 
        login_page.navigate()
        login_page.login_to_system(os.getenv("FAIL_EMAIL"), os.getenv("FAIL_PASS"))
        expect(page.get_by_text("404")).to_be_visible(timeout=5000)
    except AssertionError:
        page.context.clear_cookies()
        page.evaluate("window.localStorage.clear(); window.sessionStorage.clear();")
        login_page.navigate()
        ai_page.login_successful_ai(os.getenv("FAIL_EMAIL"), os.getenv("FAIL_PASS"))
        expect(page.get_by_text("404")).to_be_visible(timeout=3000)


def test_api_login(page):# TC3 API로그인 테스트
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")      
    expect(page.get_by_text("DevFlow ERP")).to_be_visible(timeout=10000)


def test_logout(page): #TC4 로그아웃 테스트
    login_page = LoginPage(page)
    ai_page = aipage(page)
    dashboard_page = DashboardPage(page) 
    try: 
        login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        login_page.navigate("#/dashboard")
        expect(page.get_by_text("Dash board").first).to_be_visible(timeout=10000)
        dashboard_page.user_menu()
        # dashboard_page.logout()
        expect(page.get_by_text("프로젝트 관리 & 배포 통합 시스템")).to_be_visible(timeout=3000)

    except AssertionError:
       page.context.clear_cookies()
       page.evaluate("window.localStorage.clear(); window.sessionStorage.clear();")
       login_page.navigate()
       login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
       login_page.navigate("#/dashboard")
       expect(page.get_by_text("Dash board").first).to_be_visible(timeout=10000)
       ai_page.logout_ai()
