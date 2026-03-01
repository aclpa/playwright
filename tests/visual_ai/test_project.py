from pages.login_page import LoginPage
from utils.ssim import SSIMChecker
from utils.yolo import AIVerifier
import os

def test_project_visual_integrity(page):
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/projects")
    page.wait_for_load_state("networkidle")
    current_shot = "testim/test/test_project.png"
    
    page.screenshot(
        path=current_shot,
        mask=[
        page.locator(".row.q-col-gutter-md").nth(1) 
        ]
    )
    similarity = SSIMChecker.check_layout(
        baseline_path="testim/baselines/win_project_baseline.png", 
        current_path=current_shot,
        diff_save_path="testim/errors/diff_project.png"
    )
    assert similarity >= 95.0, f"🚨 레이아웃 깨짐! (유사도: {similarity:.2f}%) errors 폴더를 확인하세요."
    ai = AIVerifier()

    required_classes = {0,2,3,4} 

    boxed_result_shot = "testim/debug/test_project_boxed_success.png"
    detected_classes = set(ai.get_detected_classes(
        current_shot, 
        conf=0.5, 
        save_path=boxed_result_shot  # AI가 네모 박스 쳐서 여기에 저장함!
    ))

    missing_classes = required_classes - detected_classes
    
    assert not missing_classes, f"🚨 시각적 버그 감지: 프로젝트 필수 UI가 누락되었습니다! (못 찾은 클래스 ID: {missing_classes})"