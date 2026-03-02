from .base_page import BasePage
from playwright.sync_api import expect

class SprintPage(BasePage):

    def create_sprint(self, sprint_name):
        self.click('button:has-text("New Sprint")', "New Sprint")
        self.click('label:has-text("Project *")', "Project")
        self.click('div[role="listbox"]:has-text("TEST")', "TEST")
        self.fill('label:has-text("Sprint Name *")', "Sprint Name", sprint_name)
        self.page.locator('label:has-text("Status")').nth(1).click()
        self.click('div[role="listbox"]:has-text("Active")', "Active")
        self.click('button:has-text("CREATE")', "CREATE")
        self.click(f'div:text-is("{sprint_name}")',sprint_name)
        expect(self.page.locator("text=스프린트 목표")).to_be_visible(timeout=5000)
        self.click('button:has-text("DELETE")', "DELETE")
        self.click('button:has-text("삭제")', "삭제")