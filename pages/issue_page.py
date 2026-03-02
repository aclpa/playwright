from .base_page import BasePage
from playwright.sync_api import expect

class IssuePage(BasePage):

    def create_issue(self, issue_title):
        self.click('button:has-text("New Issue")', "New Issue")
        self.fill('label:has-text("Title *")', "Title", issue_title)
        self.click('label:has-text("Project *")', "Project")
        self.page.locator('div[role="listbox"]').nth(0).click()
        self.click('button:has-text("Create")', "Create")
        self.page.locator(f'div:text-is("{issue_title}")').click()
        expect(self.page.locator(f'text={issue_title}')).to_be_visible(timeout=5000)
        self.click('button:has-text("삭제")', "삭제")
        self.click('button:has-text("삭제")', "삭제")