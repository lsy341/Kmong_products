from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pyautogui
import pyperclip
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
from datetime import datetime
from PyQt5.QtCore import QObject, QSettings
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import ctypes

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager



# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 시크릿 모드
chrome_options.add_argument('--incognito')

# service = Service(executable_path=ChromeDriverManager().install())

# pyqt 부분
import os

# 변경사항
# 로그인 접속 아이디 리스트
login_dict = {"" : ""}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "트래픽(영구제).ui"

# =========================
# GitHub Auto Updater (방법 B: 임시 update.bat로 자기 자신 교체)
# =========================
import zipfile
import tempfile
import subprocess
from pathlib import Path

import requests

# 너가 쓰는 GitHub 주소 그대로
VERSION_URL = "https://raw.githubusercontent.com/lsy341/Kmong_products/main/Kmong_selling_program/%ED%81%AC%EB%AA%BD/%EB%84%A4%EC%9D%B4%EB%B2%84_%ED%8A%B8%EB%9E%98%ED%94%BD_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8/%EC%98%81%EA%B5%AC%EC%A0%9C/version.txt"
ZIP_URL = "https://github.com/lsy341/Kmong_products/releases/download/traffic-latest/traffic-latest.zip"

def _open_console_once():
    # -w(windowed) exe에서도 필요할 때만 콘솔을 생성
    ctypes.windll.kernel32.AllocConsole()
    try:
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")
    except:
        pass

def _close_console_once(delay_sec: float = 0.8):
    # 메시지 잠깐 보여주고 콘솔 닫기
    try:
        time.sleep(delay_sec)
    except:
        pass
    try:
        ctypes.windll.kernel32.FreeConsole()
    except:
        pass

def _base_dir() -> Path:
    # exe 배포 시: exe가 있는 폴더
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # py로 실행 시: 현재 파일 폴더
    return Path(__file__).resolve().parent

def _this_exe_path() -> Path:
    # exe 배포 시: 현재 실행 중 exe
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    # py 실행 시: (개발용) 현재 py 파일
    return Path(__file__).resolve()

def _read_local_version(base: Path) -> str:
    p = base / "version.txt"
    if not p.exists():
        return "0.0.0"
    return p.read_text(encoding="utf-8").strip()

def _read_remote_version() -> str:
    r = requests.get(VERSION_URL, timeout=(5, 15))
    r.raise_for_status()
    return r.text.strip()

def _download_zip(to_path: Path, progress_cb=None) -> None:
    r = requests.get(ZIP_URL, stream=True, timeout=(5, 60))
    r.raise_for_status()

    total = r.headers.get("Content-Length")
    total = int(total) if total and total.isdigit() else None

    downloaded = 0
    last_percent = -1

    with open(to_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)

            if total:
                percent = int(downloaded * 100 / total)
                if percent != last_percent:  # 과도한 출력 방지
                    last_percent = percent
                    if progress_cb:
                        progress_cb(percent, downloaded, total)

def _safe_extract(zip_path: Path, extract_dir: Path) -> None:
    # Zip Slip 방지
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        base = extract_dir.resolve()
        for member in z.infolist():
            target = (extract_dir / member.filename).resolve()
            if not str(target).startswith(str(base)):
                raise RuntimeError(f"Unsafe zip path: {member.filename}")
        z.extractall(extract_dir)

def _pick_new_exe(extract_dir: Path, current_exe_name: str) -> Path:
    # 1) 현재 exe와 같은 이름이 zip 안에 있으면 최우선
    same = extract_dir / current_exe_name
    if same.exists():
        return same

    # 2) exe가 1개면 그걸 사용
    exes = list(extract_dir.glob("*.exe"))
    if len(exes) == 1:
        return exes[0]

    raise RuntimeError("traffic-latest.zip 안에서 교체할 exe를 찾지 못했습니다. (동일 이름 exe 또는 exe 1개만 있어야 함)")

def _write_update_bat(bat_path: Path, cur_exe: Path, staged_exe: Path, staged_ver: Path | None) -> None:
    """
    실행 중 exe는 바로 교체가 안 되므로,
    프로그램 종료 후 bat이 반복 시도하면서 교체 -> 재실행 -> bat 자가삭제
    """
    cur = str(cur_exe)
    new = str(staged_exe)

    lines = [
        "@echo off",
        "chcp 65001 >nul",
        "setlocal",
        "",
        "REM 파일 잠금이 풀릴 때까지 반복해서 교체 시도",
        ":loop",
        f'move /Y "{new}" "{cur}" >nul 2>nul',
        "if errorlevel 1 (",
        "  ping 127.0.0.1 -n 2 >nul",
        "  goto loop",
        ")",
        "",
    ]

    if staged_ver is not None and staged_ver.exists():
        ver_dst = str(cur_exe.parent / "version.txt")
        lines += [
            f'copy /Y "{str(staged_ver)}" "{ver_dst}" >nul 2>nul',
            f'del /F /Q "{str(staged_ver)}" >nul 2>nul',
            "",
        ]

    lines += [
        f'start "" "{cur}"',
        "ping 127.0.0.1 -n 2 >nul",
        f'del "%~f0" >nul 2>nul',
        "endlocal",
    ]

    bat_path.write_text("\r\n".join(lines), encoding="utf-8")

def check_and_apply_update_or_continue(log_print=True) -> None:
    base = _base_dir()
    cur_exe = _this_exe_path()

    console_opened = False

    try:
        local_v = _read_local_version(base)
        remote_v = _read_remote_version()

        # 업데이트 없음 -> 콘솔 안 띄우고 그대로 GUI 진행
        if local_v == remote_v:
            return

        # 업데이트 있음 -> 여기서만 콘솔 띄움
        _open_console_once()
        console_opened = True

        print(f"[Updater] 업데이트 감지: local={local_v}, remote={remote_v}")
        print("[Updater] 다운로드를 시작합니다...")

        def progress_cb(percent, downloaded, total):
            mb = 1024 * 1024
            # 한 줄 덮어쓰기
            print(
                f"\r[Updater] 다운로드중... {percent}% "
                f"({downloaded/mb:.1f}MB / {total/mb:.1f}MB)",
                end="",
                flush=True,
            )

        with tempfile.TemporaryDirectory(prefix="upd_", dir=str(base)) as td:
            tdir = Path(td)
            zip_path = tdir / "traffic-latest.zip"
            extract_dir = tdir / "extracted"

            _download_zip(zip_path, progress_cb=progress_cb)
            print("\n[Updater] 다운로드 완료. 압축 해제중...")

            _safe_extract(zip_path, extract_dir)
            print("[Updater] 압축 해제 완료. 교체 파일 준비중...")

            new_exe = _pick_new_exe(extract_dir, cur_exe.name)

            new_ver_txt = extract_dir / "version.txt"
            if not new_ver_txt.exists():
                new_ver_txt = None

            # 스테이징
            staged_exe = base / (cur_exe.stem + ".new.exe")
            if staged_exe.exists():
                staged_exe.unlink()
            staged_exe.write_bytes(new_exe.read_bytes())

            staged_ver = None
            if new_ver_txt is not None:
                staged_ver = base / "version.new.txt"
                if staged_ver.exists():
                    staged_ver.unlink()
                staged_ver.write_bytes(new_ver_txt.read_bytes())

            bat_path = base / "update.bat"
            if bat_path.exists():
                try:
                    bat_path.unlink()
                except:
                    pass

            _write_update_bat(bat_path, cur_exe, staged_exe, staged_ver)

        print("[Updater] 업데이트 적용을 위해 재시작합니다...")

        # 배치 실행 후 종료
        subprocess.Popen(["cmd", "/c", str(base / "update.bat")], cwd=str(base))

        # ✅ GUI 뜨기 전에 콘솔 닫고 종료
        _close_console_once(1.0)
        raise SystemExit(0)

    except SystemExit:
        raise
    except Exception as e:
        # 업데이트 실패 -> (업데이트 시도하다 콘솔을 띄웠다면) 콘솔 메시지 출력 후 닫고 계속 실행
        if log_print and console_opened:
            print("\n[Updater] 업데이트 실패(무시하고 계속 실행):", e)
            _close_console_once(1.2)
        return

check_and_apply_update_or_continue()

class secondThread(QThread):
    update = pyqtSignal(int)

    def __init__(self, input_keyword, input_blog_time, input_stay_time, input_traffic):
        super().__init__()
        self.input_keyword = input_keyword
        self.input_blog_time = input_blog_time
        self.input_stay_time = input_stay_time
        self.input_traffic = input_traffic

        
    def run(self):
        input_keyword = self.input_keyword
        input_blog_name = self.input_blog_time
        input_stay_time = self.input_stay_time
        input_traffic = self.input_traffic

        self.update.emit(-1)
        process = 0
        for j in range(input_traffic):
            
            for i in range(len(input_keyword)):
                driver = webdriver.Chrome(options=chrome_options)

                # 웹페이지 해당 주소 이동
                driver.implicitly_wait(5)
                driver.maximize_window()

                driver.get(f"https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&sm=mtb_jum&query={input_keyword[i]}")
                time.sleep(1)

                # 찾으려는 블로그의 인덱스
                index = 0

                while 1:
                    blog_names = driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")
                    blog_url = driver.find_elements(By.CSS_SELECTOR, "a.mfA6htQ3PFYdkANS")
                    # print(f"\nblog_url 길이 {len(blog_url)}\n")
                    # print(f"\nblog_names 길이 {len(blog_names)}\n")
                    # print(f"현재 인덱스 : {index}")


                    # 현재 바라보고 있는 페이지에 없을 경우
                    if index == len(blog_names):
                        # print("페이지에 없음")
                        # 다음 페이지 불러오기
                        blog_names[-1].send_keys(Keys.END)
                        time.sleep(2)
                        blog_url[-1].send_keys(Keys.CONTROL + "\n")
                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[1])
                        driver.close()
                        driver.switch_to.window(tabs[0])
                        time.sleep(2)
                        blog_names = driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")
                        blog_url = driver.find_elements(By.CSS_SELECTOR, "a.mfA6htQ3PFYdkANS")
                        time.sleep(2)
                        if index == len(blog_names):
                            print("더 이상 없음.")
                            break

                    else:
                        blog_name = blog_names[index].text.split("\n")[0]
                        if blog_name == input_blog_name[i]:
                            break
                        else:
                            blog_names = driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")
                            blog_url = driver.find_elements(By.CSS_SELECTOR, "a.mfA6htQ3PFYdkANS")
                            # print(f"인덱스 : {index}, {blog_url[index].text}, {blog_name}")
                            index += 1
                # 찾은 블로그 게시글 들어가기
                blog_url = driver.find_elements(By.CSS_SELECTOR, "a.mfA6htQ3PFYdkANS")
                # print(index)
                blog_url[index].click()

                # 체류시간
                time.sleep(input_stay_time)
                driver.close()
                self.update.emit(process)
                process += 1
            
# 로그인 클래스 생성
class first(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH), self)

        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.login_btn.clicked.connect(self.login_start)
        self.close_btn.clicked.connect(self.close)

    def login_start(self):
        global login_dict

        input_id = self.id.text()
        input_pw = self.pw.text()

        now = datetime.now()

        # 유효기간 변수 불러오기
        global limit

        if input_id in login_dict.keys():
            if input_pw == login_dict[input_id]:

                pyautogui.alert("로그인 성공")
                self.hide()
            
                # 두번째 창 연결
                mainwindow = second()
                mainwindow.exec_()

            else:
                pyautogui.alert("로그인 실패")
        else:
            pyautogui.alert("로그인 실패")

    def close(self):
        sys.exit()

# 메인 프로그램 클래스 생성
class second(QDialog):
    def __init__(self):
        
        # 유효기간 변수 불러오기
        global limit

        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH2), self)

        # 실행 버튼 클릭 이벤트
        self.start_btn.clicked.connect(self.start)
        
        # 종료 버튼 클릭 이벤트
        self.close_btn.clicked.connect(self.close)

        # 리셋 버튼 클릭 이벤트
        self.reset_btn.clicked.connect(self.reset)

        # 중지 버튼 클릭 이벤트
        self.stop_btn.clicked.connect(self.stop)

        
    
    def start(self):
        self.input_keyword = self.keyword.text().split(",")
        input_blog_name = self.blog_name.text().split(",")
        #  유효성 검사
        if len(self.input_keyword) == len(input_blog_name):
        
            for i in range(len(self.input_keyword)):
                self.input_keyword[i] = self.input_keyword[i].strip()

            for i in range(len(input_blog_name)):
                input_blog_name[i] = input_blog_name[i].strip()
            input_stay_time = self.stay_time.value()
            self.input_traffic = self.traffic.value()

            self.second_thread = secondThread(self.input_keyword, input_blog_name, input_stay_time, self.input_traffic)
            self.second_thread.update.connect(self.update_status)
            self.second_thread.start()
        else:
            pyautogui.alert("키워드 수와 블로그 이름 수를 맞춰주세요.")

    def update_status(self, i):
        print(f"update_status 호출됨: i = {i} self.input_traffic = {self.input_traffic}, len(self.input_keyword) = {len(self.input_keyword)}")
        print(f"round(((i + 1) / self.input_traffic * len(self.input_keyword)) * 100) = {round(((i + 1) / (self.input_traffic * len(self.input_keyword))) * 100)}")
        self.status.setValue(round(((i + 1) / (self.input_traffic * len(self.input_keyword))) * 100))

    def stop(self):
        self.second_thread.terminate()

            


        


    
    # 리셋 버튼 함수
    def reset(self):
        self.keyword.setText("")
        self.blog_name.setText("")
        self.stay_time.clear()
        self.traffic.clear()
        self.status.reset()

        

    # 종료 버튼 함수
    def close(self):
        sys.exit()

QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = first()
main_dialog.show()

sys.exit(app.exec_())
