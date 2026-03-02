from .base_page import BasePage
from playwright.sync_api import expect

class TeamPage(BasePage):

    def create_team(self, team_name):
        self.click('button:has-text("New Team")', "New Team")
        self.fill('label:has-text("Team Name *")', "Team Name", team_name)
        self.page.locator('label:has-text("Select Initial Members")').fill("admin")
        self.click('button:has-text("Create")', "Create")
        self.click('button:has-text("delete")', "delete")
        self.click('button:has-text("삭제")', "삭제")