import pytest
from dotenv import load_dotenv
import os
import time
import urllib.request
from urllib.error import URLError

load_dotenv()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

@pytest.fixture(scope="session", autouse=True)
def wait_for_server_ready():
    """테스트 시작 전, 라이브 서버(FE/BE)가 완전히 응답할 때까지 스마트하게 대기합니다."""
    
    # 환경 변수에서 프론트엔드 주소를 가져옵니다. (기본값 설정)
    target_url = os.getenv("BASE_URL")
    
    print(f"\n⏳ [Smart Polling] 서버가 켜질 때까지 대기 중... ({target_url})")

    max_retries = 30  # 최대 30번 찔러보기
    wait_seconds = 10 # 한 번 찔러보고 10초 쉬기 (총 5분 대기)

    for i in range(max_retries):
        try:
            # 5초 안에 응답이 오는지 서버의 문을 두드려 봅니다.
            response = urllib.request.urlopen(target_url, timeout=5)
            
            if response.getcode() == 200:
                print(f"\n서버 준비 완료 ({i+1}번 시도 만에 접속 성공. 테스트를 시작합니다)")
                return  # 👈 접속 성공 시, 여기서 대기를 끝내고 즉시 테스트 시작!
                
        except URLError:
            # 서버가 아직 켜지는 중이라 접속이 거부된 경우입니다. 당황하지 않고 넘어갑니다.
            pass
            
        print(f"[{i+1}/{max_retries}] 아직 서버가 준비되지 않았습니다. {wait_seconds}초 후 재시도...")
        time.sleep(wait_seconds)

    pytest.fail("5분이 지났지만 서버가 응답하지 않습니다.")
