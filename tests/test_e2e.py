from playwright.sync_api import Page, APIRequestContext, expect
from tests.pages.main_page import MainPage

# [TC 1] 3-Tier 기본 렌더링 검증 (Frontend -> Backend -> DB)
def test_initial_load(main_page: MainPage):
    main_page.navigate()
    expect(main_page.page_title).to_contain_text("3-Tier 맛집 큐레이션")
    expect(main_page.cards).to_have_count(4)


# [TC 2] POM 기반 카테고리 필터 및 키워드 검색 검증
def test_search_and_filter(main_page: MainPage):
    main_page.navigate()
    main_page.search_restaurants(category="한식", keyword="회식")

    expect(main_page.cards).to_have_count(1)
    assert "문래동 철공소 삼겹살" in main_page.get_card_names()


# [TC 3] 검색 결과 없음(Empty State) 엣지 케이스 UI 검증
def test_empty_search_result(main_page: MainPage):
    main_page.navigate()
    main_page.search_restaurants(keyword="존재하지않는식당9999")

    expect(main_page.cards).to_have_count(0)
    expect(main_page.empty_msg).to_be_visible()


# [TC 4] UI를 통한 신규 맛집 등록 및 DB 영속성(새로고침 유지) 검증
def test_add_restaurant_and_persistence(main_page: MainPage):
    main_page.navigate()

    status_code = main_page.add_restaurant(
        name="구로디지털단지 마라탕",
        category="중식",
        rating=4.6,
        tag="점심맛집/매운맛"
    )
    assert status_code == 201
    expect(main_page.cards).to_have_count(5)

    # 페이지 새로고침 후에도 SQLite DB에 남아있는지 확인
    main_page.page.reload()
    expect(main_page.cards).to_have_count(5)


# [TC 5] 하이브리드 테스트: API로 테스트 데이터 고속 주입 후 UI에서 검증
def test_seed_via_api_and_verify_on_ui(main_page: MainPage, api_context: APIRequestContext):
    res = api_context.post("/api/restaurants", data={
        "name": "잠실새내 숯불닭갈비",
        "category": "한식",
        "rating": 4.9,
        "ai_tag": "직관후뒤풀이/소주한잔"
    })
    assert res.status == 201

    main_page.navigate()
    main_page.search_restaurants(keyword="직관후뒤풀이")

    expect(main_page.cards).to_have_count(1)
    assert "잠실새내 숯불닭갈비" in main_page.get_card_names()


# [TC 6] 네트워크 모킹(Mocking) 및 백엔드 스키마 방어 검증
def test_error_handling_and_schema_validation(main_page: MainPage, api_context: APIRequestContext):
    # 1. API 레벨: 잘못된 평점(9.9) 전송 시 Pydantic이 422 에러로 방어하는지 검증
    bad_res = api_context.post("/api/restaurants", data={
        "name": "평점조작식당",
        "category": "한식",
        "rating": 9.9,
        "ai_tag": "버그유발"
    })
    assert bad_res.status == 422

    # 2. UI 레벨: 백엔드 GET API가 500 장애를 낼 때 프론트엔드 에러 배너가 뜨는지 검증
    main_page.page.route("**/api/restaurants*", lambda route: route.fulfill(status=500))
    main_page.navigate()
    expect(main_page.error_msg).to_be_visible()