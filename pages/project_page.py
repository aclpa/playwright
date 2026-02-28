from .base_page import BasePage
from playwright.sync_api import expect
class ProjectPage(BasePage):

    def create_project(self, project_name, project_key):
        self.page.locator('button:has-text("New Project")').click()
        self.page.locator("input[type='text'][aria-label='프로젝트 이름 *']").fill(project_name)
        self.page.locator("input[type='text'][aria-label='프로젝트 키 *']").fill(project_key)
        self.page.locator("input[role=combobox][aria-label='Team *']").click()
        self.page.locator("//span[contains(text(), '팀 테스트')]").click()
        self.page.locator('button:has-text("Create")').click()
        self.page.locator(f'div:text-is("{project_key}")').click()
        expect(self.page.locator("text=Project Statistics")).to_be_visible(timeout=5000)
        self.page.locator('button:has-text("Delete")').click()
        self.page.locator('button:has-text("Delete")').nth(1).click()
