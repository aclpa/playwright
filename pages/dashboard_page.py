from .base_page import BasePage

class DashboardPage(BasePage):
    def user_menu(self):
        self.page.locator("//button[.//div[contains(@class, 'q-avatar')]]").click()
    def profile(self):
        self.page.locator("//div[contains(text(), 'Profile')]").click()
    def logout(self):
        self.page.locator("//div[contains(text(), 'Logout')]").click()