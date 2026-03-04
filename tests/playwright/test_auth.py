from pages.login_page import LoginPage
from playwright.sync_api import expect
from pages.dashboard_page import DashboardPage
import os
import re

def test_successful_login(page):#TC1 로그인 성공 테스트   
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login_to_system(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    expect(page).to_have_url(re.compile(r".*/#/dashboard$"))


def test_api_login(page):# TC2 API로그인 테스트
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")     
    expect(page).to_have_url(re.compile(r".*/#/dashboard$"))


def test_logout(page): #TC3 로그아웃 테스트
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page) 
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard",timeout=600000)
    dashboard_page.user_menu()
    dashboard_page.logout()
    expect(page).to_have_url(re.compile(r".*/#/auth/login"))