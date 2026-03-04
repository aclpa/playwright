from .base_page import BasePage

class IssuePage(BasePage):

    def create_issue(self, issue_name):
        self.click('button:has-text("New Issue")', "New Issue")
        self.fill('label:has-text("Title *")', "Title", issue_name)
        self.click('label:has-text("Project *")', "Project")
        self.click('.q-virtual-scroll__content >> text("테스트")', "테스트")
        self.click('button:has-text("Create")', "Create")
