from pages.project_page import ProjectPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_project(page, api_request): #TC7 프로젝트 생성 테스트

    project_page = ProjectPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    project_name = fake.lexify(text="PROJECT????")
    project_key = fake.lexify(text="KET?????").upper()
    test_team = fake.lexify(text="TEAM????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    project_page.navigate("#/projects")

    team_data = {
        "name": test_team,
        "member_ids": [1]
        }
    team_response=api_request.post("api/v1/teams",data=team_data) 
    assert team_response.ok, f"팀 생성 실패: {team_response.status}"
    team_id = team_response.json().get("id")

    with page.expect_response("**/api/v1/projects") as response_info:
        project_page.create_project(project_name, project_key, test_team)
    response = response_info.value

    expect(page.get_by_text(f"{project_name}")).to_be_visible()

    project_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/projects/{project_id}")
    delete_api=api_request.delete(f"api/v1/teams/{team_id}")

    expect(delete_api).to_be_ok()