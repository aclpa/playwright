from .base_page import BasePage

class IssuePage(BasePage):

    def create_issue(self, issue_name ,test_project):
        self.click('button:has-text("New Issue")', "New Issue")
        self.fill('label:has-text("Title *")', "Title", issue_name)
        self.click('label:has-text("Project *")', "Project")
        self.click(f'div[role="listbox"]:has-text("{test_project}")', test_project)
        self.click('button:has-text("Create")', "Create")
