# tests/test_data_collection.py
from pages.login_page import LoginPage
from utils.labeler import AutoLabeler
from playwright.sync_api import expect
import os

admin_email = os.getenv("ADMIN_EMAIL")
admin_pass = os.getenv("ADMIN_PASS")

def test_collect_erp_data(page):
    """API 고속 로그인을 활용해 ERP 전역을 돌며 AI 학습 데이터를 수집합니다."""
    # 1. API 로그인으로 빠르게 대시보드 진입
    login_page = LoginPage(page)
    # 동작 수행
    login_page.api_login(admin_email, admin_pass)
    # 라벨러 준비
    labeler = AutoLabeler()
    
    # 3. 데이터 스크래핑 시작
    print("\n🚀 데이터 수집 파이프라인 가동을 시작합니다...")
    
    # [수집 포인트 1] 대시보드 화면
    labeler.collect(page, prefix="dashboard")
    
    # [수집 포인트 2] 프로젝트 목록 화면
    base_url = os.getenv("BASE_URL")
    page.goto(f"{base_url}/#/projects")
    labeler.collect(page, prefix="projects_list")
    
    # [수집 포인트 3] 설정 화면 등 필요한 곳을 계속 추가하세요!
    # page.goto(f"{base_url}/#/settings")
    # labeler.collect(page, prefix="settings")
    
    print("✅ 데이터 수집 완료! datasets 폴더를 확인하세요.")