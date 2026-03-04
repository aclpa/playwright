from pages.sprint_page import SprintPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_sprint(page, api_request): #TC7 스프린트 생성 테스트
    
    api_url = (os.getenv("API_URL"))
    sprint_page = SprintPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    sprint_name = fake.lexify(text="????")

    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))

    sprint_page.navigate("#/sprints")

    with page.expect_response("**/api/v1/sprints") as response_info:
        sprint_page.create_sprint(sprint_name)
    response = response_info.value

    expect(page.get_by_text(f"{sprint_name}")).to_be_visible()

    sprint_id = response.json().get("id")
    delete_api=api_request.delete(f"{api_url}api/v1/sprints/{sprint_id}")

    expect(delete_api).to_be_ok()
    
                    