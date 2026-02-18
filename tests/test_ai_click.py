# tests/test_ai_click.py
from pages.login_page import LoginPage
from utils.ai_locator import AILocator
import os
import time

def test_ai_navigation(page):
    """
    기존 Selector 방식이 아닌, AI 시각 인식으로 메뉴를 클릭하여 이동하는 테스트
    """
    # 1. 고속 로그인 (기존 방식 활용)
    login_page = LoginPage(page)
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_pass = os.getenv("ADMIN_PASS")
    login_page.api_login(admin_email, admin_pass)
    
    # 대시보드 로딩 대기
    page.wait_for_load_state("networkidle")
    time.sleep(2) # AI가 화면을 볼 시간을 줍니다
    
    # 2. AI 로케이터 가동
    # 모델 경로가 다르다면 AILocator("경로/best.pt")로 수정하세요
    ai = AILocator()
    
    # 3. 'link' (메뉴 링크) 찾아서 클릭 시도
    # 대시보드에는 보통 '프로젝트', '설정' 같은 링크들이 있습니다.
    # index=0 은 첫 번째 링크를 누르겠다는 뜻
    print("\n🚀 AI가 화면을 보고 링크를 클릭합니다...")
    ai.click_element(page, target_class="link", index=0)
    
    # 4. 화면이 바뀌었는지 확인
    time.sleep(2)
    print(f"결과 URL: {page.url}")
    
    # 검증용 스크린샷
    page.screenshot(path="ai_click_result.png")