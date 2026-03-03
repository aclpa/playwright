from .base_page import BasePage

class DashboardPage(BasePage):

    def user_menu(self):
        self.click('button:has-text("KE")',"KE")

    def profile(self):
        self.click('q-list:has-text("Profile")', "Profile")

    def logout(self):
        self.click('i:has-text("Logout")', "Logout")