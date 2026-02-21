import base_page

class TeamPage(base_page):
    def __init__(self, page, request_context=None):
        super().__init__(page, request_context)
        # Selectors
        self.btn_create_team = page.get_by_test_id("New Team").click()
        self.input_team_name = (By.XPATH,"//input[@aria-label='Team Name *']",)  # 팀 이름 입력필드
        self.select_team_members = (By.XPATH,"//input[@aria-label='Select Initial Members']",)  # 팀 멤버 선택 필드
        self.btn_submit = (By.XPATH,"//div[contains(@class, 'q-dialog')]//button[contains(., 'Create')]",)  # 생성 확인 버튼
    SELECT_TEAM_MEMBER_OPTION = (By.XPATH,"//div[@role='listbox']//div[contains(text(), 'test123')]",)  # 팀 멤버 선택 옵션     
    def create_team(self, team_name):
        """팀 생성 액션 플로우"""
        self.do_click(self.btn_create_team)
        self.do_fill(self.input_team_name, team_name)
        self.do_click(self.select_team_members)
        self.do_click(self.SELECT_TEAM_MEMBER_OPTION)
        self.do_click(self.btn_submit)
