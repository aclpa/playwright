# tests/data_collect.py (수정본)
import os
from pages.login_page import LoginPage
from utils.labeler import AutoLabeler

def test_mass_data_collection(page):
    """ERP의 여러 메뉴를 순회하며 100장 이상의 데이터를 자동으로 수집합니다."""
    # 1. 로그인
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    labeler = AutoLabeler()
    base_url = os.getenv("BASE_URL")

    # 2. 수집할 경로 리스트 (ERP 메뉴들을 여기에 추가하세요)
    target_paths = [
        "/#/dashboard",
        "/#/projects",
        "/#/sprints",
        "/#/issues",
        "/#/kanban",
        "/#/teams"
    ]

    print("\n🚀 윈도우 환경 데이터 수집 스프린트 시작...")

    for path in target_paths:
        print(f"📸 {path} 화면 수집 중...")
        page.goto(f"{base_url}{path}")
        
        # 한 페이지에서 여러 상태를 수집하기 위해 약간의 대기
        page.wait_for_load_state("networkidle")
        
        # [데이터 뻥튀기 전략]
        # 1. 일반 상태 수집
        labeler.collect(page, prefix=f"win_{path.strip('/#')}_normal")
        
        # 2. 브라우저 크기를 살짝 바꿔서 수집 (AI가 크기 변화에 강해짐)
        page.set_viewport_size({"width": 1024, "height": 768})
        labeler.collect(page, prefix=f"win_{path.strip('/#')}_small")

        # 원래 크기로 복구
        page.set_viewport_size({"width": 1280, "height": 720})

    print(f"✅ 수집 완료! 'datasets/images/train' 폴더를 확인하세요.")