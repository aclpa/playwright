from pages.sprint_page import SprintPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import os
from faker import Faker
import pytest
def test_create_sprint(page, api): #TC7 스프린트 생성 테스트
    
    sprint_page = SprintPage(page)
    login_page = LoginPage(page)
    fake = Faker()
    sprint_name = fake.lexify(text="????")
    login_page.api_login(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASS"))
    sprint_page.navigate("#/sprints")
    sprint_page.create_sprint(sprint_name)
    get_response = api.get("api/v1/sprints")
    assert get_response.ok, f"스프린트 목록 조회 실패: {get_response.status}"
    raw_data = get_response.json()
    sprints = []
    if isinstance(raw_data, list):
        sprints = raw_data
    elif isinstance(raw_data, dict):
        # 주로 사용되는 페이징 키워드('items', 'data', 'results')를 모두 찔러봅니다.
        sprints = raw_data.get("items") or raw_data.get("data") or raw_data.get("results") or []
    print(f"\n🔍 [디버그] 파악된 스프린트 목록 갯수: {len(sprints)}개")

    # 3. 파이썬 next()를 이용해 이름이 일치하는 첫 번째 스프린트의 ID 찾기
    sprint_id = next((s["id"] for s in sprints if s["name"] == sprint_name), None)
    
    # 4. 알아낸 ID로 정확하게 타겟팅하여 삭제 (DELETE)
    if sprint_id is not None:
        delete_response = api.delete(f"api/v1/sprints/{sprint_id}")
        expect(delete_response).to_be_ok()
        print(f"✅ 테스트 정리 완료: 스프린트 '{sprint_name}' (ID: {sprint_id}) 삭제됨")
    else:
        # 못 찾았을 경우, 터미널에 백엔드 원본 데이터를 전부 찍어주고 강제 에러 발생
        print(f"❌ [디버그] API 응답 원본: {raw_data}")
        pytest.fail(f"⚠️ 정리 실패: 방금 만든 '{sprint_name}'")
                    




    # with page.expect_response("**/api/v1/sprints") as response_info:
    #     sprint_page.create_sprint(sprint_name)
    # response = response_info.value
    # expect(response).to_be_ok()
    # new_sprint_data = response.json()
    # sprint_id = new_sprint_data.get("id")
    # delete_response = api.delete(f"api/v1/sprints/{sprint_id}")
    # expect(delete_response).to_be_ok()
