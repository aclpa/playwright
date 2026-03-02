from .base_page import BasePage
from playwright.sync_api import expect

class SprintPage(BasePage):

    def create_sprint(self, sprint_name):
        self.click('button:has-text("New Sprint")', "New Sprint")
        self.click('label:has-text("Project *")', "Project")
        self.page.locator('div[role="listbox"]').click()
        self.fill('label:has-text("Sprint Name *")', "Sprint Name", sprint_name)
        self.click('label:has-text("Status")', "Status")
        self.page.locator('div[role="listbox"]').get_by_text("Active").click()
        self.click('button:has-text("Create")', "Create")
        self.page.locator(f'div:text-is("{sprint_name}")').click()
        expect(self.page.locator("text=스프린트 목표")).to_be_visible(timeout=5000)
        self.click('button:has-text("삭제")', "삭제")
        self.click('button:has-text("삭제")', "삭제")