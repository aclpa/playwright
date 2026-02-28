from pages.login_page import LoginPage
from utils.ssim import SSIMChecker
from utils.yolo import AIVerifier
import os

def test_dashboard_visual_integrity(page):
    """대시보드 화면의 CSS 깨짐(SSIM) 및 필수 UI 렌더링(YOLO)을 검증합니다."""
    
    # 1. Playwright: 초고속으로 대시보드 진입 및 로딩 대기
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    login_page.navigate("#/dashboard")
    page.wait_for_load_state("networkidle") # 화면 렌더링 안정화 대기
    
    # 스크린샷 캡처
    current_shot = "temp_dashboard.png"
    page.screenshot(path=current_shot)

    # 2. SSIM: 화면 레이아웃이 기존과 95% 이상 일치하는지 픽셀 검증
    # (최초 실행 시 baseline이 없으면 자동으로 100점 처리 및 기준 이미지 생성)
    similarity = SSIMChecker.check_layout(
        baseline_path="baselines/win_dashboard_baseline.png", 
        current_path=current_shot,
        diff_save_path="errors/diff_dashboard.png"
    )
    assert similarity >= 95.0, f"🚨 레이아웃 깨짐! (유사도: {similarity:.2f}%) errors 폴더를 확인하세요."

    # 3. YOLO: 레이아웃은 맞더라도 필수 UI(아바타 등)가 화면에 렌더링 되었는지 AI 검증
    ai = AIVerifier()
    is_avatar_visible = ai.verify_element_exists(current_shot, target_class="avatar", conf=0.5)
    assert is_avatar_visible, "🚨 시각적 버그: 우측 상단 아바타가 화면에 보이지 않습니다!"