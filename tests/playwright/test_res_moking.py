from pages.login_page import LoginPage
from playwright.sync_api import expect
import os


def test_gets_the_json_from_api_and_adds_a_new_fruit(page):
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))    
    
    def handle(route):
        response = route.fetch()
        json = response.json()
        json["items"].append({"id": 999, "name": "Loquat", "slug": "loquat", "avatar_url": None, "member_count": 1}) # items 리스트에 .append = 리스트 마지막에 추가 
        json["meta"]["total"] += 1 # meta = 팀 카드를 제외한 나머지 ui 없으면 로딩이 안됨 item에 하나 추가했으니 +1
        route.fulfill(response=response, json=json)

    page.route("**/api/v1/teams*", handle)

    # Go to the page
    login_page.navigate("#/teams")

    # Assert that the new fruit is visible
    expect(page.get_by_text("Loquat", exact=True)).to_be_visible()