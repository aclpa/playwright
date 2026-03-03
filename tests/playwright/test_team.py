from pages.team_page import TeamPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os

from faker import Faker

def test_create_team(page, api): #TC8 팀 생성 테스트
    team_page = TeamPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    team_name = fake.lexify(text="????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    team_page.navigate("#/teams")
    with page.expect_response("**/api/v1/teams") as response_info:
        team_page.create_team(team_name)
    response = response_info.value
    new_team_data = response.json()
    team_id = new_team_data.get("id")
    api.delete(f"api/v1/teams/{team_id}")

    