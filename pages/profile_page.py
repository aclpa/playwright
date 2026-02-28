from .base_page import BasePage
class ProfilePage(BasePage):

    def edit_profile(self, username, Full_Name, Phone, Avatar_Url):
        self.page.locator("button:has-text('Edit Profile')").click()
        self.page.locator("label:has-text('Username *')").fill(username)
        self.page.locator("label:has-text('Full Name *')").fill(Full_Name)
        self.page.locator("label:has-text('Phone *')").fill(Phone)
        self.page.locator("label:has-text('Avatar URL')").fill(Avatar_Url)
        self.page.locator("button:has-text('UPDATE')").click()