from .base_page import BasePage
from playwright.sync_api import expect

class KanbanPage(BasePage): 

    def drag_and_drop(self):

        card = self.page.locator('div.issue-card:has-text("drag_and_drop_test")')
        target = self.page.locator('div.kanban-column:has-text("In Progress")')
        card.wait_for(state="visible")
        card.drag_to(target)
        expect(target.locator('div.issue-card:has-text("drag_and_drop_test")')).to_be_visible()
