from pages.team_page import TeamPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re
from faker import Faker

def test_create_team(page): #TC8 팀 생성 테스트
    team_page = TeamPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    team_name = fake.lexify(text="팀 ????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    team_page.navigate("#/teams")
    team_page.create_team(team_name)
    expect(page).to_have_url(re.compile(r".*/#/teams$"))