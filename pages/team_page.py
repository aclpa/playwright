from .base_page import BasePage
from playwright.sync_api import expect

class TeamPage(BasePage):

    def create_team(self, team_name):
        self.page.locator('button:has-text("New Team")').click()
        self.page.locator('label:has-text("Team Name *")').fill(team_name)
        self.page.locator('label:has-text("Select Initial Members")').fill("admin")
        self.page.locator('button:has-text("Create")').click()
        self.page.locator('button:has-text("delete")').nth(0).click()
        self.page.locator('button:has-text("삭제")').click()
