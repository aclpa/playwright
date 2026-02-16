import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.api_client import get_api_token

@pytest.fixture(scope="session")
def browser_fix(browser_context_args):
    """
    Playwright의 기본 브라우저 컨텍스트 설정을 오버라이드합니다.
    모든 테스트는 이 설정을 공통으로 상속받습니다.
    """
    return {
        **browser_context_args,
        # Task 1.2: AI 인식률 최적화를 위한 1280x720 고정 해상도
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        # 고정 스케일 팩토리: OS별 고해상도 모니터(Retina 등)로 인한 픽셀 배수 차이 방지
        "device_scale_factor": 1,
        # 유저 에이전트 표준화: 브라우저 지문 차이로 인한 UI 변경 방지
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
