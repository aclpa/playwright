from pages.ai_page import aipage
from playwright.sync_api import expect
from pages.login_page import LoginPage
import re
import os

admin_email = os.getenv("ADMIN_EMAIL")
admin_pass = os.getenv("ADMIN_PASS")
base_url = os.getenv("BASE_URL")   

def test_ai(page):
    ai_page = aipage(page)
    login_page = LoginPage(page)
    login_page.navigate()
    ai_page.login_successful_ai(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    expect(page.get_by_text("Dash board").first).to_be_visible(timeout=3000)

def test_ai_logout(page):   
    ai_page = aipage(page)
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")
    expect(page.get_by_text("Dash board").first).to_be_visible(timeout=10000)
    ai_page.logout_ai()


# def test_ai_navigation(page):
#     """
#     YOLO와 OCR이 결합된 하이브리드 AI로 메뉴를 찾아 클릭하는 테스트
#     """
#     # 1. api 로그인
#     login_page = LoginPage(page)

    
#     print("\n🌐 시스템 로그인 중...")
#     login_page.api_login(admin_email, admin_pass)
#     # AI 로케이터
#     ai = AILocator()
#     # 3. AI에게 특정 텍스트를 가진 요소 클릭 지시
#     print("\n🚀 AI가 화면을 스캔하여 타겟을 찾습니다...")
#     # [미션 2] 왼쪽 메뉴에서 "Projects" 찾아 누르기
#     print("\n--- [미션 2] 왼쪽 메뉴 클릭 ---")
#     page.wait_for_selector("text=Projects", timeout=5000)
#     ai.click_by_text(page, target_text="Projects", target_class="link", conf=0.5)
#     print("\n--- [미션 1] 새 프로젝트 버튼 클릭 ---")
#     page.wait_for_selector("text=New Project", timeout=5000)
#     ai.click_by_text(page, target_text="NEW PROJECT", target_class="button", conf=0.5)
#     print("✅ 모든 AI 네비게이션 테스트 완료!")
