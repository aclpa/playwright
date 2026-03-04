from .base_page import BasePage

class ProfilePage(BasePage):

    def edit_profile(self, phone, avatar_url):
        self.click("button:has-text('Edit Profile')", "Edit Profile")
        self.fill("label:has-text('Phone *')", "Phone", phone)
        self.fill("label:has-text('Avatar URL')", "Avatar URL", avatar_url)
        self.click("button:has-text('UPDATE')", "UPDATE")
