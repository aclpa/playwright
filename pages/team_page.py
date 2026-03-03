from .base_page import BasePage
from playwright.sync_api import expect
import json

class TeamPage(BasePage):

    def create_team(self, team_name):
        self.click('button:has-text("New Team")', "New Team")
        self.fill('label:has-text("Team Name *")', "Team Name", team_name)
        self.fill('label:has-text("Select Initial Members")',"Select Initial Members","admin")
        self.click('button:has-text("Create")', "Create")
        
