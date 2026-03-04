from .base_page import BasePage
from playwright.sync_api import expect

class KanbanPage(BasePage): 

    def drag_and_drop(self, test_issue):

        card = self.page.locator(f'div.issue-card:has-text("{test_issue}")')
        target = self.page.locator('div.kanban-column:has-text("In Progress")')
        card.wait_for(state="visible")
        card.drag_to(target)
        expect(target.locator(f'div.issue-card:has-text("{test_issue}")')).to_be_visible()
