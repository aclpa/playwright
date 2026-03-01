from pages.login_page import LoginPage
from utils.ssim import SSIMChecker
from utils.yolo import AIVerifier
import os

def test_toolbar(page):

    login_page = LoginPage(page)
    ai=AIVerifier()
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")
    page.wait_for_load_state("networkidle")

    toolbar_locator = page.locator(".q-toolbar.row.no-wrap.items-center")
    toolbar_shot = "testim/regions/toolbar.png"
    toolbar_locator.screenshot(path=toolbar_shot)

    required_classes = {3} 
    yolo_debug_shot = "testim/debug/toolbar_yolo_result.png"

    detected_classes = set(ai.get_detected_classes(
        image_path=toolbar_shot, 
        conf=0.5, 
        save_path=yolo_debug_shot
    ))

    missing_classes = required_classes - detected_classes
    assert not missing_classes, f"🚨 AI 시각 검증 실패: 대시보드 필수 UI 누락! (못 찾은 클래스 ID: {missing_classes})"

    

    similarity_toolbar = SSIMChecker.check_layout(
        baseline_path="testim/baselines/win_toolbar.png",
        current_path=toolbar_shot,
        diff_save_path="testim/errors/diff_toolbar.png"
    )
    assert similarity_toolbar >= 98.0, f"상태 카드 영역 레이아웃 이상 ({similarity_toolbar:.2f}%)"