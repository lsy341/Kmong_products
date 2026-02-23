import time
import pyautogui
import pyperclip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

pyautogui.FAILSAFE = True


# =========================
# 설정
# =========================
# ✅ 포스팅용 텔레그램 봇 토큰(파이썬 봇 전용) - 네가 쓰는 봇 토큰 넣기
BOT_TOKEN = "여기에_포스팅봇_토큰_넣기"

# ✅ 네이버 계정(원하면 하드코딩 가능)
NAVER_ID = None
NAVER_PW = None

# =========================
# 유틸
# =========================
def normalize(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")

def clip_paste(text: str):
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)

def parse_message_to_title_body(raw: str) -> tuple[str, str]:
    """
    입력 형식:
    [제목]
    ...
    [본문]
    ...
    """
    t = normalize(raw).strip()

    if "[제목]" not in t or "[본문]" not in t:
        raise ValueError("형식 오류: [제목] / [본문] 섹션이 필요합니다.")

    title_part = t.split("[제목]", 1)[1]
    title = title_part.split("[본문]", 1)[0].strip()
    body = title_part.split("[본문]", 1)[1].strip()

    if not title:
        raise ValueError("형식 오류: 제목이 비어있습니다.")
    if not body:
        raise ValueError("형식 오류: 본문이 비어있습니다.")

    return title, body


# =========================
# 네이버 자동화
# =========================
def naver_login(driver, user_id: str, user_pw: str):
    driver.implicitly_wait(5)
    driver.maximize_window()
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")
    time.sleep(1.2)

    id_el = driver.find_element(By.CSS_SELECTOR, "#id")
    id_el.click()
    id_el.clear()
    clip_paste(user_id)

    pw_el = driver.find_element(By.CSS_SELECTOR, "#pw")
    pw_el.click()
    pw_el.clear()
    clip_paste(user_pw)

    driver.find_element(By.CSS_SELECTOR, "#log\\.login").click()
    time.sleep(2)

    try:
        driver.find_element(By.CSS_SELECTOR, "#new\\.save").click()
        time.sleep(1)
    except NoSuchElementException:
        pass

    if "nid.naver.com" in driver.current_url:
        print("⚠️ 추가 인증/캡차 처리 후 Enter")
        input()

def go_write(driver, user_id: str):
    driver.get(f"https://blog.naver.com/{user_id}?Redirect=Write&")
    time.sleep(4)

def dismiss_write_popups(driver):
    # ⭐ 2번 반복
    for _ in range(2):
        try:
            WebDriverWait(driver, 8).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
            )
        except TimeoutException:
            return

        # 도움말 패널
        try:
            btn = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
            if btn.is_displayed():
                btn.click()
                time.sleep(0.3)
        except Exception:
            pass

        # 팝업 취소 버튼
        try:
            btns = driver.find_elements(By.CSS_SELECTOR, ".se-popup-button-cancel")
            for b in btns:
                try:
                    if b.is_displayed():
                        b.click()
                        time.sleep(0.3)
                except Exception:
                    pass
        except Exception:
            pass

        driver.switch_to.default_content()
        time.sleep(0.5)

def input_title_body_by_index(driver, title: str, body: str):
    """
    .se-text-paragraph 결과가 2개:
      [0] 제목
      [1] 본문
    """
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
    )

    elems = driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")
    if len(elems) < 2:
        driver.switch_to.default_content()
        raise RuntimeError(f".se-text-paragraph 요소가 {len(elems)}개입니다. (최소 2개 필요)")

    title_el = elems[0]
    body_el = elems[1]

    # 제목 입력
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title_el)
    time.sleep(0.2)
    ActionChains(driver).move_to_element_with_offset(title_el, 10, 10).click().perform()
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    clip_paste(title)

    # 본문 입력
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", body_el)
    time.sleep(0.2)
    ActionChains(driver).move_to_element_with_offset(body_el, 10, 10).click().perform()
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    clip_paste(normalize(body))

    driver.switch_to.default_content()

def click_save_and_close(driver):
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
    )

    try:
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".save_btn__bzc5B"))
        )
        save_btn.click()
        time.sleep(2)
        print("💾 저장 버튼 클릭 완료")
    except Exception as e:
        print(f"⚠️ 저장 버튼 클릭 실패: {type(e).__name__}: {e}")

    driver.switch_to.default_content()

    driver.quit()
    print("🧹 브라우저 종료 완료")


def naver_post_from_raw(raw_text: str):
    global NAVER_ID, NAVER_PW

    title, body = parse_message_to_title_body(raw_text)

    if not NAVER_ID or not NAVER_PW:
        raise RuntimeError("NAVER_ID / NAVER_PW가 설정되어야 합니다.")

    driver = webdriver.Chrome()
    naver_login(driver, NAVER_ID, NAVER_PW)
    go_write(driver, NAVER_ID)

    dismiss_write_popups(driver)
    input_title_body_by_index(driver, title, body)
    click_save_and_close(driver)

    print("✅ 전체 완료")


# =========================
# (봇 없이) 콘솔 입력 테스트용
# =========================
if __name__ == "__main__":
    NAVER_ID = input("네이버 ID: ").strip()
    NAVER_PW = input("네이버 PW: ").strip()

    print("\n아래 형식으로 원고 전체를 붙여넣고, 마지막에 엔터 2번(빈 줄 2개) 입력하세요.\n")
    lines = []
    blank = 0
    while True:
        line = input()
        if line == "":
            blank += 1
            if blank >= 2:
                break
        else:
            blank = 0
        lines.append(line)

    raw = "\n".join(lines).strip()
    naver_post_from_raw(raw)
