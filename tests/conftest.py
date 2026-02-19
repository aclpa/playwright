# tests/conftest.py
import pytest
from dotenv import load_dotenv

# 테스트 시작 전 환경 변수(.env) 가장 먼저 로드
load_dotenv()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Playwright의 기본 브라우저 컨텍스트 설정을 오버라이드합니다.
    (함수 이름을 반드시 'browser_context_args'로 해야 자동 적용됩니다!)
    """
    return {
        **browser_context_args,
        
        # 💡 AI 인식률 최적화를 위한 1280x720 고정 해상도 (필수)
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        
        # 고정 스케일 팩토리: OS별 고해상도 모니터(Retina 등)로 인한 픽셀 배수 차단
        "device_scale_factor": 1,
        
        # 유저 에이전트 표준화: 브라우저 지문 차이로 인한 UI 변경(모바일 뷰 등) 방지
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }