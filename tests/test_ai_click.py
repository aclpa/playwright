# tests/test_ai_click.py
import os
import time
from pages.login_page import LoginPage
from utils.ai_locator import AILocator

def test_ai_navigation(page):
    """
    YOLO와 OCR이 결합된 하이브리드 AI로 메뉴를 찾아 클릭하는 테스트
    """
    # 1. api 로그인
    login_page = LoginPage(page)
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_pass = os.getenv("ADMIN_PASS")
    
    print("\n🌐 시스템 로그인 중...")
    login_page.api_login(admin_email, admin_pass)

    # 대시보드 로딩 대기
    page.wait_for_load_state("networkidle")
    time.sleep(2) # 화면 렌더링 안정화 대기

    # AI 로케이터
    ai = AILocator()

    # 3. AI에게 특정 텍스트를 가진 요소 클릭 지시
    print("\n🚀 AI가 화면을 스캔하여 타겟을 찾습니다...")
    
    # [미션 1] "NEW PROJECT" 버튼 찾아 누르기
    print("\n--- [미션 1] 새 프로젝트 버튼 클릭 ---")
    ai.click_by_text(page, target_text="NEW PROJECT", target_class="button", conf=0.01)
    
    page.wait_for_timeout(2000) # 클릭 후 화면 전환 대기
    
    # 원래 대시보드로 복귀
    page.go_back()
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # [미션 2] 왼쪽 메뉴에서 "Projects" 찾아 누르기
    print("\n--- [미션 2] 왼쪽 메뉴 클릭 ---")
    ai.click_by_text(page, target_text="Projects", target_class="link", conf=0.01)
    
    page.wait_for_timeout(2000)
    print("✅ 모든 AI 네비게이션 테스트 완료!")