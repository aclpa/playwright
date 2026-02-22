from pages.login_page import LoginPage
from playwright.sync_api import expect
from pages.ai_page import aipage
import os

def test_successful_login(page):#TC1 로그인 성공 테스트   
    login_page = LoginPage(page)
    ai_page = aipage(page) 
    try: 
        login_page.login_to_system(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        expect(page.get_by_text("Dash board").first).to_be_visible(timeout=3000)
    except AssertionError:
        ai_page.login_successful_ai(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        expect(page.get_by_text("Dash board").first).to_be_visible(timeout=3000)


def test_failed_login(page): #TC2 로그인 실패 테스트
    login_page = LoginPage(page)
    ai_page = aipage(page) 
    try: 
        login_page.login_to_system(os.getenv("FAIL_EMAIL"), os.getenv("FAIL_PASS"))
        expect(page.get_by_text("404")).to_be_visible(timeout=3000)
    except AssertionError:
        ai_page.login_successful_ai(os.getenv("FAIL_EMAIL"), os.getenv("FAIL_PASS"))
        expect(page.get_by_text("404")).to_be_visible(timeout=3000)


def test_api_login(page):# TC3 API로그인 테스트
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))      
    expect(page.get_by_text("DevFlow ERP")).to_be_visible(timeout=10000)

def test_logout(page): #TC4 로그아웃 테스트
    login_page = LoginPage(page)
    ai_page = aipage(page) 
    try: 
        login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        

    except AssertionError:
        ai_page.login_successful_ai(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
        page.locator("button[aria-label='User menu']").click()
        page.locator("text=Logout").click()
        expect(page.get_by_text("Login")).to_be_visible(timeout=3000)
