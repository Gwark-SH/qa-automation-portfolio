from playwright.sync_api import Page, Locator

class MainPage:
    URL = "http://localhost:8080"

    def __init__(self, page: Page):
        self.page = page
        self.page_title: Locator = page.get_by_test_id("page-title")

        # 로그인 관련 로케이터
        self.username_input: Locator = page.get_by_test_id("username-input")
        self.password_input: Locator = page.get_by_test_id("password-input")
        self.login_btn: Locator = page.get_by_test_id("login-btn")
        self.logout_btn: Locator = page.get_by_test_id("logout-btn")
        self.welcome_msg: Locator = page.get_by_test_id("welcome-msg")
        self.auth_notice: Locator = page.get_by_test_id("auth-notice")

        # 검색/필터 로케이터
        self.category_select: Locator = page.get_by_test_id("category-select")
        self.search_input: Locator = page.get_by_test_id("search-input")
        self.search_btn: Locator = page.get_by_test_id("search-btn")
        
        # 신규 등록 폼 로케이터
        self.new_name: Locator = page.get_by_test_id("new-name")
        self.new_category: Locator = page.get_by_test_id("new-category")
        self.new_rating: Locator = page.get_by_test_id("new-rating")
        self.new_tag: Locator = page.get_by_test_id("new-tag")
        self.add_btn: Locator = page.get_by_test_id("add-btn")

        # 동적 상태 메시지 및 리스트 로케이터
        self.toast_msg: Locator = page.get_by_test_id("toast-msg")
        self.loading_spinner: Locator = page.get_by_test_id("loading-spinner")
        self.cards: Locator = page.get_by_test_id("restaurant-card")
        self.empty_msg: Locator = page.get_by_test_id("empty-msg")
        self.error_msg: Locator = page.get_by_test_id("error-msg")

    def navigate(self):
        self.page.goto(self.URL)

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def search_restaurants(self, category: str = "전체", keyword: str = ""):
        self.category_select.select_option(category)
        self.search_input.fill(keyword)
        self.search_btn.click()

    def add_restaurant(self, name: str, category: str, rating: float, tag: str) -> int:
        self.new_name.fill(name)
        self.new_category.select_option(category)
        self.new_rating.fill(str(rating))
        self.new_tag.fill(tag)

        with self.page.expect_response("**/api/restaurants") as response_info:
            self.add_btn.click()
        return response_info.value.status

    def get_card_names(self) -> list[str]:
        return self.cards.get_by_test_id("card-name").all_inner_texts()