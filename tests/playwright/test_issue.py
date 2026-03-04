from pages.issue_page import IssuePage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_issue(page, api_request): #TC4 이슈 생성 테스트

    api_url = (os.getenv("API_URL"))
    issue_page = IssuePage(page)
    login_page = LoginPage(page)
    fake = Faker()
    issue_name = fake.lexify(text="????")

    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    issue_page.navigate("#/issues")

    with page.expect_response("**/api/v1/issues") as response_info:
        issue_page.create_issue(issue_name)
    response = response_info.value

    expect(page.get_by_text(f"{issue_name}")).to_be_visible()

    issue_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/issues/{issue_id}")

    expect(delete_api).to_be_ok()

    