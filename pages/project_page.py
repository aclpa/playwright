from .base_page import BasePage

class ProjectPage(BasePage):

    def create_project(self, project_name, project_key,test_team):
        self.click('button:has-text("project")', "Project")
        self.fill('label:has-text("프로젝트 이름 *")',"프로젝트 이름",project_name)
        self.fill('label:has-text("프로젝트 키 *")',"프로젝트 키",project_key)
        self.click("input[role=combobox][aria-label='Team *']", "Team")
        self.click(f'.q-virtual-scroll__content >> text="{test_team}"', test_team)
        self.click('button:has-text("Create")', "Create")
