from pages.team_page import TeamPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
from faker import Faker
import os

def test_create_team(page, api_request): #TC9 팀 생성 테스트
    
    team_page = TeamPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    team_name = fake.lexify(text="##????##")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    
    team_page.navigate("#/teams")
    page.wait_for_load_state("networkidle")
    with page.expect_response("**/api/v1/teams",timeout=60000) as response_info:
        team_page.create_team(team_name)
    response = response_info.value

    expect(page.get_by_text(f"{team_name}")).to_be_visible()

    team_id = response.json().get("id")
    delete_api=api_request.delete(f"api/v1/teams/{team_id}")
        
    expect(delete_api).to_be_ok()
    

