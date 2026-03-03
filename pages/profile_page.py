from .base_page import BasePage

class ProfilePage(BasePage):

    def edit_profile(self, full_name, phone, avatar_url):
        self.click("button:has-text('Edit Profile')", "Edit Profile")
        self.fill("label:has-text('Full Name *')", "Full Name", full_name)
        self.fill("label:has-text('Phone *')", "Phone", phone)
        self.fill("label:has-text('Avatar URL')", "Avatar URL", avatar_url)
        self.click("button:has-text('UPDATE')", "UPDATE")

    def profile_team(self):
        self.click("button:has-text('dark_mode')", "dark_mode")
        self.click("a:has-text('Teams')", "Teams")