from pages.base_page import BasePage
from utils.ai_locator import AILocator
import time
class aipage(BasePage):

    def login_successful_ai(self, email, password):
        ai = AILocator()
        self.navigate()
        time.sleep(5)  # 페이지 로딩 대기
        ai.click_by_text(self.page, target_text="이메일", target_class="input", conf=0.5)
        self.page.keyboard.type(email)
        ai.click_by_text(self.page, target_text="비밀번호", target_class="input", conf=0.5)
        self.page.keyboard.type(password)
        ai.click_by_text(self.page, target_text="로그인", target_class="button", conf=0.5)
        