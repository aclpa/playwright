from pages.issue_page import IssuePage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_issue(page, api_request): #TC4 이슈 생성 테스트

    issue_page = IssuePage(page)
    login_page = LoginPage(page)
    fake = Faker()
    issue_name = fake.lexify(text="????")
    test_team = fake.lexify(text="????")
    test_project = fake.lexify(text="????")
    test_project_key = fake.lexify(text="????").upper()
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))

    team_data = {
        "name": test_team,
        "member_ids": [1]
        }
    team_response=api_request.post("api/v1/teams",data=team_data) 
    assert team_response.ok, f"팀 생성 실패: {team_response.status}"
    team_id = team_response.json().get("id")

    project_data = {
        "name": test_project,
        "key": test_project_key,
        "team_id": team_id
        }
    project_response=api_request.post("api/v1/projects",data=project_data) 
    assert project_response.ok, f"프로젝트 생성 실패: {project_response.status}"

    issue_page.navigate("#/issues")

    with page.expect_response("**/api/v1/issues") as response_info:
        issue_page.create_issue(issue_name,test_project)
    response = response_info.value

    expect(page.get_by_text(f"{issue_name}")).to_be_visible()

    issue_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/issues/{issue_id}")
    delete_api=api_request.delete(f"api/v1/teams/{team_id}")

    expect(delete_api).to_be_ok()

    