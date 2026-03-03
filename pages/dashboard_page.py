from .base_page import BasePage

class DashboardPage(BasePage):

    def user_menu(self):
        self.click("//button[.//div[contains(@class, 'q-avatar')]]","avatar",timeout=240000)

    def profile(self):
        self.click("//div[contains(text(), 'Profile')]", "Profile")

    def logout(self):
        self.click("//div[contains(text(), 'Logout')]", "Logout")