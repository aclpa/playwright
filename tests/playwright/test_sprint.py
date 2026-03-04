from pages.sprint_page import SprintPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_create_sprint(page, api_request): #TC8 스프린트 생성 테스트
    
    sprint_page = SprintPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    sprint_name = fake.lexify(text="????")
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
    assert team_response.ok, f"프로젝트 생성 실패: {project_response.status}"

    sprint_page.navigate("#/sprints")
    with page.expect_response("**/api/v1/sprints", timeout=60000) as response_info:
        sprint_page.create_sprint(sprint_name, test_project)
    response = response_info.value

    expect(page.get_by_text(f"{sprint_name}")).to_be_visible()

    sprint_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/sprints/{sprint_id}")
    delete_api=api_request.delete(f"api/v1/teams/{team_id}")

    expect(delete_api).to_be_ok()
    
                    