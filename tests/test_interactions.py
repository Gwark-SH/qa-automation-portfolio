import time
from playwright.sync_api import Page, expect
from tests.pages.main_page import MainPage

# [TC 1] 비로그인 상태의 UI 잠금(Disabled) 검증
def test_guest_ui_disabled_state(main_page: MainPage):
    main_page.navigate()
    
    # 비로그인 시 등록 버튼과 입력창이 비활성화(disabled) 상태여야 함
    expect(main_page.add_btn).to_be_disabled()
    expect(main_page.new_name).to_be_disabled()
    expect(main_page.auth_notice).to_be_visible()


# [TC 2] 로그인 성공 시 상태 변화(UI 활성화 + 토스트 알림 + localStorage 토큰) 검증
def test_login_and_toast_lifecycle(main_page: MainPage):
    main_page.navigate()
    main_page.login("qa_admin", "pass1234")

    # 1. 환영 문구가 뜨고, 잠겨있던 등록 버튼이 활성화(Enabled)되는지 확인
    expect(main_page.welcome_msg).to_have_text("qa_admin님 환영합니다")
    expect(main_page.add_btn).to_be_enabled()

    # 2. 토스트 알림이 화면에 즉시 나타났다가 -> 3초 이내에 스스로 사라지는지(Hidden) 동적 검증
    expect(main_page.toast_msg).to_be_visible()
    expect(main_page.toast_msg).to_have_text("로그인되었습니다.")
    expect(main_page.toast_msg).to_be_hidden(timeout=4000)

    # 3. 브라우저 localStorage에 실제로 토큰이 저장되었는지 JS 평가(evaluate)로 검증
    token = main_page.page.evaluate("() => window.localStorage.getItem('qa_token')")
    assert token == "secret-qa-token-2026"


# [TC 3] ★실무 꿀팁★ UI 로그인 과정을 생략하고 토큰을 직접 주입(Bypass)해 시간 단축하기
def test_bypass_ui_login_with_storage_injection(main_page: MainPage):
    # 페이지가 열리기 전에 localStorage에 토큰을 미리 꽂아 넣는 스크립트 등록
    main_page.page.add_init_script("""
        window.localStorage.setItem('qa_token', 'secret-qa-token-2026');
        window.localStorage.setItem('qa_user', 'qa_admin');
    """)
    
    # 접속하자마자 이미 로그인된 상태(버튼 활성화)로 렌더링되는지 확인!
    main_page.navigate()
    expect(main_page.add_btn).to_be_enabled()
    expect(main_page.welcome_msg).to_be_visible()


# [TC 4] 브라우저 네이티브 Confirm 알림창 제어 및 삭제 동작 검증
def test_delete_restaurant_with_confirm_dialog(main_page: MainPage):
    # 토큰 주입으로 빠른 로그인 상태 진입
    main_page.page.add_init_script("""
        window.localStorage.setItem('qa_token', 'secret-qa-token-2026');
        window.localStorage.setItem('qa_user', 'qa_admin');
    """)
    main_page.navigate()
    expect(main_page.cards).to_have_count(4)

    # 브라우저 confirm 창이 뜨면 자동으로 '확인(accept)'을 누르도록 이벤트 리스너 등록
    main_page.page.on("dialog", lambda dialog: dialog.accept())

    # 첫 번째 카드의 [삭제] 버튼 클릭
    first_card_delete_btn = main_page.cards.first.get_by_test_id("delete-btn")
    first_card_delete_btn.click()

    # 삭제 토스트가 뜨고 카드가 3개로 줄어들었는지 검증
    expect(main_page.toast_msg).to_have_text("삭제되었습니다.")
    expect(main_page.cards).to_have_count(3)


# [TC 5] 네트워크 지연(Latency) 발생 시 '로딩 스피너' 노출 검증
def test_loading_spinner_on_slow_network(main_page: MainPage):
    # API 응답을 강제로 1.5초 지연시키는 핸들러 등록
    def slow_api(route):
        time.sleep(1.5)
        route.continue_()

    main_page.page.route("**/api/restaurants*", slow_api)
    main_page.navigate()

    # 응답이 오기 전에는 로딩 스피너가 눈에 보여야 함
    expect(main_page.loading_spinner).to_be_visible()
    # 1.5초 뒤 응답이 도착하면 스피너가 사라지고 카드가 4개 떠야 함
    expect(main_page.loading_spinner).to_be_hidden(timeout=3000)
    expect(main_page.cards).to_have_count(4)