from .base_page import BasePage
from playwright.sync_api import expect

class KanbanPage(BasePage): 

    def drag_and_drop(self):
        todo_column = self.page.locator('div.kanban-column:has-text("To Do")')
        card = todo_column.locator('div.issue-card:has-text("테스트")')
        expect(todo_column).to_be_visible(timeout=5000)

        if card.count() > 0:
            card.drag_to(self.page.locator('div.kanban-column:has-text("In Progress")'))
        else:
            self.page.locator('div.issue-card:has-text("테스트")').drag_to(self.page.locator('div.kanban-column:has-text("To Do")'))
