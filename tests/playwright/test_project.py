from pages.project_page import ProjectPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_project(page, api_request): #TC7 프로젝트 생성 테스트

    api_url = (os.getenv("API_URL"))
    project_page = ProjectPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    project_name = fake.lexify(text="????")
    project_key = fake.lexify(text="?????").upper()

    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    project_page.navigate("#/projects")

    with page.expect_response("**/api/v1/projects") as response_info:
        project_page.create_project(project_name, project_key)
    response = response_info.value

    expect(page.get_by_text(f"{project_name}")).to_be_visible()

    project_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/projects/{project_id}")

    expect(delete_api).to_be_ok()