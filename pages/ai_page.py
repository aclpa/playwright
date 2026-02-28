from pages.base_page import BasePage
from erp_qa.utils.yolo import YOLO

class aipage(BasePage):

    def login_successful_ai(self, email, password):
        ai = YOLO()
        self.page.wait_for_selector("text=이메일", timeout=3000)
        if ai.click_by_text(self.page, target_text="이메일", target_class="input", conf=0.5):
            self.page.keyboard.type(email)
        if ai.click_by_text(self.page, target_text="비밀번호", target_class="input", conf=0.5):
            self.page.keyboard.type(password)
        ai.click_by_text(self.page, target_text="로그인", target_class="button", conf=0.5, exact_match=True)

    def logout_ai(self):
        ai = YOLO()
        ai.click_by_text(self.page, target_text="AD", target_class="avatar", conf=0.5)
        ai.click_by_text(self.page, target_text="Logout", target_class="link", conf=0.5, exact_match=True)
        
    
    def project_ai(self):
        ai = YOLO()
        ai.click_by_text(self.page, target_text="NEW PROJECT", target_class="button", conf=0.5)
        ai.click_by_text(self.page, target_text="이름", target_class="input", conf=0.5)
        ai.click_by_text(self.page, target_text="Team", target_class="q-select", conf=0.5)