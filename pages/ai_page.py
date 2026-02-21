from base_page import BasePage
from utils.ai_locator import AILocator

class ai_page(BasePage):

    def login_successful_ai(page):
        ai = AILocator()
        page.wait_for_selector("text=Projects", timeout=5000)
        ai.click_by_text(page, target_text="Projects", target_class="link", conf=0.5)
        