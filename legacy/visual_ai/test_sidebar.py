from pages.login_page import LoginPage
from legacy.ssim import SSIMChecker
from utils.yolo import AIVerifier
import os

def test_sidebar(page):

    login_page = LoginPage(page)
    ai=AIVerifier()
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")
    page.wait_for_load_state("networkidle")
    
    sidebar_locator = page.locator(".q-list.q-list--padding") 
    sidebar_shot = "testim/regions/sidebar.png"
    sidebar_locator.screenshot(path=sidebar_shot)

    required_classes = {2} 
    yolo_debug_shot = "testim/debug/sidebar_yolo_result.png"

    detected_classes = set(ai.get_detected_classes(
        image_path=sidebar_shot, 
        conf=0.5, 
        save_path=yolo_debug_shot
    ))

    missing_classes = required_classes - detected_classes
    assert not missing_classes, f"🚨 AI 시각 검증 실패: 대시보드 필수 UI 누락! (못 찾은 클래스 ID: {missing_classes})"

    similarity_sidebar = SSIMChecker.check_layout(
        baseline_path="testim/baselines/win_sidebar.png",
        current_path=sidebar_shot,
        diff_save_path="testim/errors/diff_sidebar.png"
    )
    assert similarity_sidebar >= 98.0, f"메뉴 영역 레이아웃 이상({similarity_sidebar:.2f}%)"



