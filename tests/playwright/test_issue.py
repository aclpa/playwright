from pages.issue_page import IssuePage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
import re
from faker import Faker

def test_create_issue(page): #TC6 이슈 생성 테스트
    issue_page = IssuePage(page)
    login_page = LoginPage(page)
    fake = Faker()
    issue_title = fake.lexify(text="이슈 ????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    issue_page.navigate("#/issues")
    issue_page.create_issue(issue_title)
    expect(page).to_have_url(re.compile(r".*/#/issues$"))