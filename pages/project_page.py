from .base_page import BasePage
from playwright.sync_api import expect

class ProjectPage(BasePage):

    def create_project(self, project_name, project_key):
        self.click('button:has-text("project")', "Project")
        self.fill('area-label:has-text("프로젝트 이름 *")',"프로젝트 이름",project_name)
        self.page.locator("input[type='text'][aria-label='프로젝트 키 *']").fill(project_key)
        self.click("input[role=combobox][aria-label='Team *']", "Team")
        self.page.locator("//span[contains(text(), '팀 테스트')]").click()
        self.click('button:has-text("Create")', "Create")
        self.click(f'div:text-is("{project_key}")',f"{project_key}")
        expect(self.page.locator("text=Project Statistics")).to_be_visible(timeout=5000)
        self.click('button:has-text("Delete")', "Delete")
        self.click('button:has-text("삭제")',"삭제")