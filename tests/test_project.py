from pages.project_page import ProjectPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re
from faker import Faker

def test_create_project(page): #TC5 프로젝트 생성 테스트
    project_page = ProjectPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    project_name = fake.lexify(text="프로젝트 ????")
    project_key = fake.lexify(text="?????").upper()
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    project_page.navigate("#/projects")
    project_page.create_project(project_name, project_key)
    expect(page).to_have_url(re.compile(r".*/#/projects$"))