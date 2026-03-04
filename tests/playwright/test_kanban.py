from pages.kanban_page import KanbanPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_drag_and_drop(page, api_request): #TC5 드래그 엔 드롭 테스트
    kanban_page = KanbanPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    test_team = fake.lexify(text="TEA????")
    test_project = fake.lexify(text="PRO????")
    test_project_key = fake.lexify(text="KOQ????").upper()
    test_issue = fake.lexify(text="ISS????")
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
    project_id = project_response.json().get("id")


    issue_data = {
    "title": test_issue,
    "project_id": project_id
    }
    api_request.post("api/v1/issues",data=issue_data) 

    kanban_page.navigate("#/kanban")
    kanban_page.drag_and_drop(test_issue)

    delete_api=api_request.delete(f"api/v1/teams/{team_id}")
    expect(delete_api).to_be_ok()
    