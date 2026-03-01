from pages.kanban_page import KanbanPage
from pages.login_page import LoginPage
import os

def test_drag_and_drop(page): #TC10 드래그 엔 드롭 테스트
    kanban_page = KanbanPage(page)
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    kanban_page.navigate("#/kanban")
    kanban_page.drag_and_drop()
