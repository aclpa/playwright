from .base_page import BasePage
from playwright.sync_api import expect

class IssuePage(BasePage):

    def create_issue(self, issue_title):
        self.click('button:has-text("New Issue")', "New Issue")
        self.fill('label:has-text("Title *")', "Title", issue_title)
        self.click('label:has-text("Project *")', "Project")
        self.click('div[role="listbox"]:has-text("테스트")', "테스트")
        self.click('button:has-text("Create")', "Create")
        self.click(f'div:text-is("{issue_title}")',issue_title)
        expect(self.page.locator('text=수정일')).to_be_visible(timeout=5000)
        self.click('button:has-text("DELETE")', "DELETE")
        self.click('button:has-text("삭제")', "삭제")