import pytest
from playwright.sync_api import APIRequestContext, Playwright, Page
from tests.pages.main_page import MainPage

BACKEND_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> APIRequestContext:
    """백엔드 API를 직접 호출하는 Playwright API 클라이언트"""
    context = playwright.request.new_context(base_url=BACKEND_URL)
    yield context
    context.dispose()

@pytest.fixture(autouse=True)
def reset_db_before_each_test(api_context: APIRequestContext):
    """각 테스트 실행 직전마다 DB를 초기 시드 데이터(4개) 상태로 리셋"""
    res = api_context.post("/api/test/reset")
    assert res.ok, "DB 초기화 실패: 백엔드 서버(Port 8000)가 실행 중인지 확인하세요."

@pytest.fixture
def main_page(page: Page) -> MainPage:
    """테스트 함수에 MainPage 객체를 바로 주입해주는 Fixture"""
    return MainPage(page)