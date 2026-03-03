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