from .base_page import BasePage

class ProjectPage(BasePage):

    def create_project(self, project_name, project_key):
        self.click('button:has-text("project")', "Project")
        self.fill('area-label:has-text("프로젝트 이름 *")',"프로젝트 이름",project_name)
        self.fill('area-label:has-text("프로젝트 키 *")',"프로젝트 키",project_key)
        self.click("input[role=combobox][aria-label='Team *']", "Team")
        self.click('.q-virtual-scroll__content >> text="팀 테스트"', "팀 테스트")
        self.click('button:has-text("Create")', "Create")
