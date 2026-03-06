from .base_page import BasePage

class SprintPage(BasePage):

    def create_sprint(self, sprint_name, test_project):
        self.click('button:has-text("New Sprint")', "New Sprint")
        self.click('label:has-text("Project *")', "Project")
        self.click(f'div[role="listbox"]:has-text("{test_project}")', test_project)
        self.fill('aria-label-label:has-text("Sprint Name *")', "Sprint Name *", sprint_name)
        self.page.locator('label:has-text("Status")').nth(1).click()
        self.click('.q-virtual-scroll__content >> text="Active"', "Active")
        self.click('button:has-text("CREATE")', "CREATE")