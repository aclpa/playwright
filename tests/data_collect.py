import os
from pages.login_page import LoginPage
from utils.labeler import AutoLabeler

def test_data_collect(page):
    login_page = LoginPage(page)
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    labeler = AutoLabeler()
    base_url = os.getenv("BASE_URL")

   
    target_paths = [
        "/#/auth/login",
        "/#/dashboard",
        "/#/projects",
        "/#/sprints",
        "/#/issues",
        "/#/kanban",
        "/#/teams",
        "/#/resources/servers",
        "/#/resources/services",
        "/#/profile",
        "/#/resources/deployments"
    ]

    for path in target_paths:
        prefix = path.replace("/", "_").replace("#", "") 
    
        page.goto(f"{base_url}{path}")
        page.wait_for_load_state("networkidle")
    
        labeler.collect(page, prefix=f"win_{prefix}_normal")
    
        page.set_viewport_size({"width": 1280, "height": 768})
        labeler.collect(page, prefix=f"win_{prefix}_small")
    
        page.set_viewport_size({"width": 1000, "height": 500})
        labeler.collect(page, prefix=f"win_{prefix}_mobile")

        page.set_viewport_size({"width": 1920, "height": 1080})
        labeler.collect(page, prefix=f"win_{prefix}_large")

        page.set_viewport_size({"width": 1280, "height": 720})

    page.goto(f"{base_url}/#/dashboard")
    page.locator("//button[.//div[contains(@class, 'q-avatar')]]").click()
    page.wait_for_timeout(500)
    labeler.collect(page, prefix="win_profile_dropdown")
    page.set_viewport_size({"width": 1000, "height": 700})
    labeler.collect(page, prefix="win_profile_dropdown_small")

    page.goto(f"{base_url}/#/projects")
    page.locator('button:has-text("New Project")').click()
    labeler.collect(page, prefix="win_new_project")
    page.set_viewport_size({"width": 1080, "height": 720})
    labeler.collect(page, prefix="win_new_project_small")
    page.set_viewport_size({"width": 800, "height": 1200})
    labeler.collect(page, prefix="win_new_project_mobile")

    page.goto(f"{base_url}/#/Issues")
    page.locator('button:has-text("New Issue")').click()
    labeler.collect(page, prefix="win_new_issue")
    page.set_viewport_size({"width": 1080, "height": 720})
    labeler.collect(page, prefix="win_new_issue_small")
    page.set_viewport_size({"width": 800, "height": 1200})
    labeler.collect(page, prefix="win_new_issue_mobile")

    page.goto(f"{base_url}/#/Teams")
    page.locator('button:has-text("New Team")').click()
    labeler.collect(page, prefix="win_new_team")
    page.set_viewport_size({"width": 1080, "height": 720})
    labeler.collect(page, prefix="win_new_team_small")
    page.set_viewport_size({"width": 800, "height": 1200})
    labeler.collect(page, prefix="win_new_team_mobile")

    page.goto(f"{base_url}/#/Sprints")
    page.locator('button:has-text("New Sprint")').click()
    labeler.collect(page, prefix="win_new_sprint")
    page.set_viewport_size({"width": 1080, "height": 720})
    labeler.collect(page, prefix="win_new_sprint_small")
    page.set_viewport_size({"width": 800, "height": 1200})
    labeler.collect(page, prefix="win_new_sprint_mobile")
    
    page.goto(f"{base_url}/#/profile")
    page.locator('button:has-text("Edit Profile")').click()
    labeler.collect(page, prefix="win_edit_profile")
    page.set_viewport_size({"width": 1080, "height": 720})
    labeler.collect(page, prefix="win_edit_profile_small")
    page.set_viewport_size({"width": 800, "height": 1200})
    labeler.collect(page, prefix="win_edit_profile_mobile")
    