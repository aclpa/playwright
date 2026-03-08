from pages.login_page import LoginPage
from playwright.sync_api import expect
import os



def test_mock_the_fruit_api(page):
    api_url  = os.getenv("API_URL")
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))    
    
    def handle(route, request):
        if request.method == "GET" and "/api/v1/teams" in request.url:
            route.fulfill(json={
                "items": [{"id": 999, "name": "Strawberry", "slug": "strawberry", "avatar_url": None, "member_count": 1}],
                "meta": {
                    "total": 1,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
            }
        })
        else:
            route.continue_()
    # Intercept the route to the fruit API
    page.route("**/api/v1/teams*", handle)

    # Go to the page
    login_page.navigate("#/teams")
    # Assert that the Strawberry fruit is visible
    expect(page.get_by_text("Strawberry")).to_be_visible()