import time
import asyncio
import pyautogui
import pyperclip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

def force_front_selenium_only(driver):
    """Selenium만으로 크롬을 앞으로/활성화 '시도' (100% 보장 X)"""
    # 1) CDP: 앞으로 가져오기
    try:
        driver.execute_cdp_cmd("Browser.bringToFront", {})
    except Exception:
        pass


    # 3) 위치/크기 재설정으로 앞으로 나오게 유도
    try:
        driver.set_window_rect(x=0, y=0, width=1200, height=900)
        time.sleep(0.2)
    except Exception:
        pass

pyautogui.FAILSAFE = True


# =========================
# ✅ 설정: 토큰/네이버 계정
# =========================
BOT_TOKEN = "8358829457:AAHuhZm0J3w-YNj5yYhyRtdLM5GZWeo7GGg"

NAVER_ID = "nkingseoul"
NAVER_PW = "qmffhrm1@"

# 종료 키워드 (원고 끝 판단)
END_KEYWORD = "감사합니다!"


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
    driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")

    # ✅ 로그인 때만 포커스 유도
    force_front_selenium_only(driver)
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

    # 브라우저 등록: 있으면 클릭, 없으면 패스
    try:
        save_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#new\\.save"))
        )
        save_btn.click()
        time.sleep(1)
    except TimeoutException:
        pass

    if "nid.naver.com" in driver.current_url:
        print("⚠️ 추가 인증/캡차 처리 후 콘솔에서 Enter")
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

    # 제목
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title_el)
    time.sleep(0.2)
    ActionChains(driver).move_to_element_with_offset(title_el, 10, 10).click().perform()
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    clip_paste(title)

    # 본문
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
    title, body = parse_message_to_title_body(raw_text)

    driver = webdriver.Chrome()
    naver_login(driver, NAVER_ID, NAVER_PW)
    go_write(driver, NAVER_ID)

    dismiss_write_popups(driver)
    input_title_body_by_index(driver, title, body)
    click_save_and_close(driver)


# =========================
# 텔레그램 봇 상태
# =========================
# user_id -> {"waiting": bool, "buffer": str}
STATE = {}
POST_LOCK = asyncio.Lock()

def st(user_id: int):
    if user_id not in STATE:
        STATE[user_id] = {"waiting": False, "buffer": ""}
    return STATE[user_id]


# =========================
# 텔레그램 핸들러
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 포스팅 봇입니다.\n\n"
        "사용법:\n"
        "1) /wait 입력\n"
        "2) [제목]...[본문]... 원고를 여러 번 나눠 보내도 됨\n"
        f"3) 누적 텍스트에 '{END_KEYWORD}'가 포함되면 자동으로 포스팅 실행\n\n"
        "명령:\n"
        "/wait  대기 시작\n"
        "/cancel  대기/버퍼 초기화\n"
        "/status  현재 누적 길이 확인\n"
    )

async def cmd_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = st(update.effective_user.id)
    s["waiting"] = True
    s["buffer"] = ""
    await update.message.reply_text(
        f"✅ 대기 시작!\n원고를 보내줘. '{END_KEYWORD}'가 들어오면 그걸 끝으로 자동 실행할게."
    )

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = st(update.effective_user.id)
    s["waiting"] = False
    s["buffer"] = ""
    await update.message.reply_text("🧹 초기화 완료. 다시 /wait 하면 대기합니다.")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = st(update.effective_user.id)
    await update.message.reply_text(
        f"waiting={s['waiting']}\n누적 글자수={len(s['buffer'])}"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_obj = update.effective_message
    if not msg_obj:
        return

    user = update.effective_user
    if not user:
        return

    user_id = user.id
    s = st(user_id)

    # 대기 모드가 아니면 안내만 하고 종료 (봇은 계속 실행)
    if not s["waiting"]:
        await msg_obj.reply_text("지금은 대기 상태가 아니야. /wait 먼저 입력해줘.")
        return

    try:
        msg = msg_obj.text or ""

        # 누적 (메시지 단위로 줄바꿈 하나 붙여서 합침)
        if s["buffer"]:
            s["buffer"] += "\n" + msg
        else:
            s["buffer"] = msg

        # 아직 끝 키워드가 없으면 계속 대기
        if END_KEYWORD not in s["buffer"]:
            await msg_obj.reply_text(f"📥 추가 수신 완료. '{END_KEYWORD}' 나오면 자동 실행할게.")
            return

        # 끝 키워드가 들어왔으면 실행
        raw = s["buffer"]
        s["buffer"] = ""
        s["waiting"] = False

        await msg_obj.reply_text("✅ 원고 끝(감사합니다) 감지! 네이버 포스팅 시작합니다...")

        async with POST_LOCK:
            try:
                # 무거운 작업은 thread로
                await asyncio.to_thread(naver_post_from_raw, raw)

                await msg_obj.reply_text("✅ 완료! (저장 버튼 클릭 + 브라우저 종료까지 끝)")
                # 성공이면 대기 종료 상태 유지 (원하면 여기서 자동 wait로 바꿀 수도 있음)
                return

            except Exception as e:
                # ✅ 실패 이유 전송 + 다시 wait 모드로 복귀
                err_msg = f"{type(e).__name__}: {e}"
                s["waiting"] = True      # 다시 대기
                s["buffer"] = ""         # 버퍼는 초기화(원하면 유지로 바꿔줄 수 있음)
                await msg_obj.reply_text(
                    "❌ 포스팅 실패!\n"
                    f"사유: {err_msg}\n\n"
                    "✅ 다시 대기 모드로 돌아갔어. 원고를 처음부터 다시 보내줘!"
                )
                return

    except Exception as e:
        # handle_text 자체에서 터지는 예외도 방어: 이유 보내고 다시 wait 복귀
        err_msg = f"{type(e).__name__}: {e}"
        s["waiting"] = True
        s["buffer"] = ""
        await msg_obj.reply_text(
            "⚠️ 처리 중 오류가 발생했지만 봇은 계속 실행 중이야.\n"
            f"사유: {err_msg}\n\n"
            "✅ 다시 대기 모드로 돌아갔어. 원고를 다시 보내줘!"
        )


def main():
    if not BOT_TOKEN or "여기에_" in BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN에 실제 텔레그램 봇 토큰을 넣어주세요.")
    if not NAVER_ID or not NAVER_PW or "여기에_" in NAVER_ID or "여기에_" in NAVER_PW:
        raise RuntimeError("NAVER_ID / NAVER_PW에 실제 네이버 계정을 넣어주세요.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wait", cmd_wait))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 포스팅 봇 실행 중... (텔레그램에서 /wait 후 원고 전송)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
