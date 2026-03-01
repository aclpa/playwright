import os
from pages.login_page import LoginPage
from utils.labeler import AutoLabeler

def test_mass_data_collection(page):
    """ERP의 각 세부 컴포넌트(사이드바, 헤더, 툴바 등)만 집중적으로 수집합니다."""
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    labeler = AutoLabeler()
    base_url = os.getenv("BASE_URL")

    print("\n🧩 완전 세분화(Component-level) 데이터 수집 시작...")

    # 1. 대시보드 페이지 이동
    page.goto(f"{base_url}/#/dashboard")
    page.wait_for_load_state("networkidle")

    # --- [구역 1] 사이드바 (Sidebar) 수집 ---
    sidebar_locator = page.locator(".q-drawer") # 실제 사이드바 클래스로 변경 필요
    if sidebar_locator.is_visible():
        labeler.collect(page, prefix="comp_sidebar_normal", target_locator=sidebar_locator)
        # 반응형 테스트를 위해 창 크기를 줄여서 사이드바 다시 캡처
        page.set_viewport_size({"width": 1000, "height": 700})
        labeler.collect(page, prefix="comp_sidebar_small", target_locator=sidebar_locator)
        page.set_viewport_size({"width": 1280, "height": 720}) # 원상복구

    # --- [구역 2] 상단 헤더/툴바 (Toolbar) 수집 ---
    header_locator = page.locator(".q-header") # 실제 헤더 클래스로 변경 필요
    if header_locator.is_visible():
        labeler.collect(page, prefix="comp_header", target_locator=header_locator)

    # --- [구역 3] 대시보드 중앙 위젯 영역 수집 ---
    # 예: Total Projects 등이 있는 상단 상태 카드 묶음
    status_cards_locator = page.locator(".row.q-col-gutter-md").first()
    if status_cards_locator.is_visible():
        labeler.collect(page, prefix="comp_dashboard_cards", target_locator=status_cards_locator)

    # 2. 프로젝트 페이지 이동
    page.goto(f"{base_url}/#/projects")
    page.wait_for_load_state("networkidle")
    
    # --- [구역 4] 프로젝트 리스트/그리드 영역 수집 ---
    project_list_locator = page.locator(".q-table__container") # 실제 테이블 클래스로 변경 필요
    if project_list_locator.is_visible():
        labeler.collect(page, prefix="comp_project_list", target_locator=project_list_locator)

    print(f"✅ 세분화된 컴포넌트 수집 완료! 'datasets/images/train' 폴더를 확인하세요.")