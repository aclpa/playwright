from pages.project_page import ProjectPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re

def test_create_project(page):
    project_page = ProjectPage(page)
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    project_page.navigate("#/projects")
    project_page.create_project("Test Project", "TP")
    expect(page).to_have_url(re.compile("projects"))