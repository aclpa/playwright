from pages.login_page import LoginPage
from utils.api_client import get_api_token
from playwright.sync_api import Playwright
import time
def test_successful_login(page): #TC1 로그인 성공 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행 
    login_page.login_to_system("admin@devflow.com", "devpassword")
    # 3. 결과 검증
    assert "/dashboard" in page.url

def test_failed_login(page): #TC2 로그인 실패 테스트
    # 1. 페이지 객체 초기화
    login_page = LoginPage(page)
    # 2. 동작 수행 
    login_page.login_to_system("admin@devflow.com", "wrongpassword")
    # 3. 결과 검증
    wait_for_error = page.wait_for_selector("span.error-code strong", state="visible")
    assert wait_for_error is not None



# POST /users/login API 테스트
def test_api_login(page, playwright: Playwright):
    page.goto("https://erp-sut.vercel.app/#/projects/")
    api_context = playwright.request.new_context()
    api_url = "https://erp-backend-api-ww9v.onrender.com" 

    # 1. API로 로그인 요청
    response = api_context.post(
        f"{api_url}/api/v1/auth/login",
        data={
            "email": "admin@devflow.com",
            "password": "devpassword", 
        }
    )

    print(f"Response Status: {response.status}")
    assert response.status == 200 # 실패하면 여기서 멈춤

    # 2. 로그인 성공 응답에서 데이터 추출
    body = response.json() 
    print("Response Body:", body)

    # ==========================================
    # 💡 [핵심 해결책] 브라우저(page)에 로그인 정보 주입하기
    # ==========================================
    
    # 주의: 응답 JSON 구조에 따라 'token', 'access_token' 등 키 이름이 다를 수 있습니다.
    # print된 body 내용을 확인하고 알맞은 키를 넣으세요.
    token = body.get("token") 

    # 브라우저 스토리지에 접근하려면 먼저 해당 도메인의 아무 페이지나 열려있어야 합니다.
    page.goto("https://erp-sut.vercel.app/") 

    # 프론트엔드가 사용하는 스토리지 키(예: 'token', 'jwt', 'user')에 값을 세팅합니다.
    # (개발자 도구 F12 -> Application -> Local Storage에서 정확한 Key 이름을 확인해야 합니다)
    page.evaluate(f"window.localStorage.setItem('token', '{token}');")
    
    # (만약 앱이 쿠키를 쓴다면 위 evaluate 대신 아래 코드를 씁니다)
    # page.context.add_cookies(api_context.cookies())

    # ==========================================

    # 3. 이제 권한이 생겼으므로 진짜 가고 싶은 페이지로 이동
    page.goto("https://erp-sut.vercel.app/#/projects/")
    time.sleep(5) # 페이지 로딩 대기 (실무에서는 page.wait_for_selector() 권장)

    # 이동 후 현재 URL이 projects가 맞는지 검증
    assert "projects" in page.url



