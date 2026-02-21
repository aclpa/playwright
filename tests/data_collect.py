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

    # 2. 수집할 경로 리스트
    target_paths = [
        "/#/dashboard",
        "/#/projects",
        "/#/sprints",
        "/#/issues",
        "/#/kanban",
        "/#/teams",
        "/#/resources/servers",
        "/#/resources/services",
        "/#/profile",
        "/#/resources/deployments"
    ]

    print("\n🚀 윈도우 환경 데이터 수집 스프린트 시작...")

    for path in target_paths:
        prefix = path.replace("/", "_").replace("#", "")  # ← 수정
    
        page.goto(f"{base_url}{path}")
        page.wait_for_load_state("networkidle")
    
        labeler.collect(page, prefix=f"win_{prefix}_normal")
    
        page.set_viewport_size({"width": 1280, "height": 768})
        labeler.collect(page, prefix=f"win_{prefix}_small")
    
        page.set_viewport_size({"width": 1000, "height": 500})
        labeler.collect(page, prefix=f"win_{prefix}_mobile")

        page.set_viewport_size({"width": 1920, "height": 1080})
        labeler.collect(page, prefix=f"win_{prefix}_large")

        page.set_viewport_size({"width": 1280, "height": 720})

    print(f"✅ 수집 완료! 'datasets/images/train' 폴더를 확인하세요.")