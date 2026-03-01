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
    current_shot = "testim/test/test_dashboard.png"
 
    page.screenshot(
        path=current_shot,
        mask=[page.locator(".q-list.q-list--separator")
              ] # 배열 형태로 여러 개 지정 가능
    )

    # 2. SSIM: 화면 레이아웃이 기존과 95% 이상 일치하는지 픽셀 검증
    # (최초 실행 시 baseline이 없으면 자동으로 100점 처리 및 기준 이미지 생성)
    similarity = SSIMChecker.check_layout(
        baseline_path="testim/baselines/win_dashboard_baseline.png", 
        current_path=current_shot,
        diff_save_path="testim/errors/diff_dashboard.png"
    )
    assert similarity >= 95.0, f"🚨 레이아웃 깨짐! (유사도: {similarity:.2f}%) errors 폴더를 확인하세요."

    # 3. YOLO: 레이아웃은 맞더라도 필수 UI(아바타 등)가 화면에 렌더링 되었는지 AI 검증
    ai = AIVerifier()
    # 💡 [핵심] 대시보드 화면이라면 반드시 있어야 할 필수 클래스 ID를 지정합니다.
    # (예: 2번(link/메뉴), 3번(avatar/프로필)) -> 버튼이나 입력창은 페이지에 따라 변할 수 있으니 제외
    required_classes = {2, 3} 
    
    # AI가 사진 한 장을 보고 찾아낸 모든 클래스 ID를 집합(Set)으로 가져옵니다.
    detected_classes = set(ai.get_detected_classes(current_shot, conf=0.5))
    
    # 우리가 원하는 필수 요소가 AI가 찾은 결과에 모두 포함되어 있는지 수학의 '차집합'으로 뺍니다.
    missing_classes = required_classes - detected_classes
    
    # 만약 누락된 클래스가 하나라도 있다면(missing_classes가 비어있지 않다면) 에러를 뱉습니다!
    assert not missing_classes, f"🚨 시각적 버그 감지: 대시보드 필수 UI가 누락되었습니다! (못 찾은 클래스 ID: {missing_classes})"