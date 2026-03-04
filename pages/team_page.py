from .base_page import BasePage

class TeamPage(BasePage):

    def create_team(self, team_name):
        self.click('button:has-text("New Team")', "New Team")
        self.fill('label:has-text("Team Name *")', "Team Name", team_name)
        self.click('button:has-text("Create")', "Create")
        
