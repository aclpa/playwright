from pages.project_page import ProjectPage
from pages.login_page import LoginPage
import os

def test_create_project(page):
    project_page = ProjectPage(page)
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    project_page.navigate("#/projects")
    project_page.create_project("Test Project", "TP")