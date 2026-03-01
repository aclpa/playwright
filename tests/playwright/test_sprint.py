from pages.sprint_page import SprintPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re
from faker import Faker

def test_create_sprint(page): #TC7 스프린트 생성 테스트
    sprint_page = SprintPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    sprint_name = fake.lexify(text="스프린트 ????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    sprint_page.navigate("#/sprints")
    sprint_page.create_sprint(sprint_name)
    expect(page).to_have_url(re.compile(r".*/#/sprints$"))