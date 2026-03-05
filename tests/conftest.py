import pytest
from dotenv import load_dotenv
import os
import time
import urllib.request
from urllib.error import URLError
import pytest
from typing import Generator
from playwright.sync_api import Playwright, APIRequestContext

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
                response = urllib.request.urlopen(target_url, timeout=5)
                if response.getcode() == 200:
                    print(f"\n서버 준비 완료: {target_url} ({i+1}번 시도)")
                    break
            except URLError:
                pass
            print(f"[{i+1}/{max_retries}] 대기 중: {target_url}, {wait_seconds}초 후 재시도")
            time.sleep(wait_seconds)
        else:
            pytest.fail(f"5분이 지났지만 서버가 응답하지 않습니다: {target_url}")


@pytest.fixture(scope="module")
def api_request(playwright: Playwright) -> Generator[APIRequestContext, None, None]:

    api_url = (os.getenv("API_URL"))
    login_request = playwright.request.new_context(base_url=api_url)
    login_data = {
        "email": os.getenv("ADMIN_EMAIL"),
        "password": os.getenv("ADMIN_PASS")
    }
    response=login_request.post(f"{api_url}api/v1/auth/login", data=login_data)
    ACCESS_TOKEN=response.json().get("access_token")
    login_request.dispose()
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    request_context = playwright.request.new_context(
        base_url=(os.getenv("API_URL")),extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()
