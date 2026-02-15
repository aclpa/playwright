from pages.login_page import LoginPage

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
