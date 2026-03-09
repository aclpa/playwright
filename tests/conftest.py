import pytest
from dotenv import load_dotenv
import os
import time
import urllib.request
from urllib.error import URLError
import pytest
from typing import Generator
from playwright.sync_api import Playwright, APIRequestContext
import allure
from playwright.sync_api import Page

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
    targets = [
        os.getenv("API_URL") + "ready",
        os.getenv("BASE_URL"),
    ]
    max_retries = 30
    wait_seconds = 10

    for target_url in targets:       
        for i in range(max_retries):
            try:
                response = urllib.request.urlopen(target_url, timeout=120)
                if response.getcode() == 200:
                    print(f"\n서버 준비 완료: {target_url} ({i+1}번 시도)")
                    break
            except Exception as e:
                print(f"[{i+1}/{max_retries}] 대기 중: {target_url} ({e})")
                time.sleep(wait_seconds)
        else:                         
            pytest.fail(f"서버가 응답하지 않습니다: {target_url}")


@pytest.fixture(scope="module")
def api_request(playwright: Playwright) -> Generator[APIRequestContext, None, None]:

    api_url = (os.getenv("API_URL"))
    login_request = playwright.request.new_context(base_url=api_url) #백엔드와 통신용 기본 메서드 base_url에 .env api_url 삽입
    login_data = {
        "email": os.getenv("ADMIN_EMAIL"),
        "password": os.getenv("ADMIN_PASS")
    }                                                         
    response=login_request.post("api/v1/auth/login", data=login_data) # 로그인 post 보내서 access_tkoen 받아오기
    ACCESS_TOKEN=response.json().get("access_token") # 파이썬이 읽을 수 있는 json으로 변환한 뒤 access_token 가져옴
    login_request.dispose() # 메모리 삭제
    headers = { 
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    request_context = playwright.request.new_context(
        base_url=api_url,extra_http_headers=headers # 기본 메서드에 headers
    )
    yield request_context #test 로 보내기 위해 정지하고 반환
    request_context.dispose()




@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(page: Page, request):
    yield
    if request.node.rep_call.failed:
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="실패 스크린샷",
            attachment_type=allure.attachment_type.PNG
        )