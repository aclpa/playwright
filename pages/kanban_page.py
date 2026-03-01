from .base_page import BasePage
from playwright.sync_api import expect

class KanbanPage(BasePage): 

    def drag_and_drop(self):
        to_do_column = self.page.locator('div.kanban-column:has-text("To Do")')
        card = to_do_column.locator('div.issue-card:has-text("테스트")')
        expect(to_do_column).to_be_visible(timeout=5000)

        if card.count() > 0:
            card.drag_to(self.page.locator('div.kanban-column:has-text("In Progress")'))
        else:
            self.page.locator('div.issue-card:has-text("테스트")').drag_to(self.page.locator('div.kanban-column:has-text("To Do")'))
