from .base_page import BasePage
from playwright.sync_api import expect

class IssuePage(BasePage):

    def create_issue(self, issue_title):
        self.page.locator('button:has-text("New Issue")').click()
        self.page.locator('label:has-text("Title *")').fill(issue_title)
        self.page.locator('label:has-text("Project *")').click()
        self.page.locator('div[role="listbox"]').nth(0).click()
        self.page.locator('button:has-text("Create")').click()
        self.page.locator(f'div:text-is("{issue_title}")').click()
        expect(self.page.locator(f'text={issue_title}')).to_be_visible(timeout=5000)
        self.page.locator('button:has-text("삭제")').click()
        self.page.locator('button:has-text("삭제")').nth(1).click()

