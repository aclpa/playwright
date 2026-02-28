from .base_page import BasePage
from playwright.sync_api import expect

class SprintPage(BasePage):

    def create_sprint(self, sprint_name):
        self.page.locator('button:has-text("New Sprint")').click()
        self.page.locator('label:has-text("Project *")').click()
        self.page.locator('div[role="listbox"]').click()
        self.page.locator('label:has-text("Sprint Name *")').fill(sprint_name)
        self.page.locator('label:has-text("Status")').nth(1).click()
        self.page.locator('div[role="listbox"]').get_by_text("Active").click()
        self.page.locator('button:has-text("Create")').click()
        self.page.locator(f'div:text-is("{sprint_name}")').click()
        expect(self.page.locator("text=스프린트 목표")).to_be_visible(timeout=5000)
        self.page.locator('button:has-text("삭제")').click()
        self.page.locator('button:has-text("삭제")').nth(1).click()