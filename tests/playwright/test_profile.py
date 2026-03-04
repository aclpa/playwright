from pages.profile_page import ProfilePage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker

def test_edit_profile(page): #TC6 프로필 수정 테스트
    profile_page = ProfilePage(page)
    login_page = LoginPage(page)
    fake = Faker()
    phone = fake.phone_number()
    avatar_url = fake.image_url()
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    profile_page.navigate("#/profile")
    profile_page.edit_profile(phone, avatar_url)
    expect(page.get_by_text("Administrator")).to_be_visible(timeout=5000)

