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
import random
import traceback
from PyQt5.QtCore import QSettings
from datetime import datetime
from datetime import timedelta
from PyQt5.QtCore import QObject, QSettings
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# # 불필요한 에러 메시지 없애기
# chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# service = Service(executable_path=ChromeDriverManager().install())

# pyqt 부분
import os

# =========================
# GitHub Auto Updater (방법 B: 임시 update.bat로 자기 자신 교체)
# =========================
import zipfile
import tempfile
import subprocess
from pathlib import Path

import requests

# 너가 쓰는 GitHub 주소 그대로
VERSION_URL = "https://raw.githubusercontent.com/lsy341/Kmong_products/main/Kmong_selling_program/%ED%81%AC%EB%AA%BD/%EC%84%9C%EC%9D%B4%EC%B6%94_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8/%EC%98%81%EA%B5%AC%EC%A0%9C/version.txt"
ZIP_URL = "https://raw.githubusercontent.com/lsy341/Kmong_products/main/Kmong_selling_program/%ED%81%AC%EB%AA%BD/%EC%84%9C%EC%9D%B4%EC%B6%94_%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8/%EC%98%81%EA%B5%AC%EC%A0%9C/latest.zip"

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

def _download_zip(to_path: Path) -> None:
    r = requests.get(ZIP_URL, stream=True, timeout=(5, 60))
    r.raise_for_status()
    with open(to_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

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

    raise RuntimeError("latest.zip 안에서 교체할 exe를 찾지 못했습니다. (동일 이름 exe 또는 exe 1개만 있어야 함)")

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
    """
    - 버전 다르면 latest.zip 다운로드
    - 새 exe를 base_dir에 *.new.exe로 스테이징
    - update.bat 실행
    - 현재 프로세스 종료(배치가 교체 후 재실행)
    """
    base = _base_dir()
    cur_exe = _this_exe_path()

    try:
        local_v = _read_local_version(base)
        remote_v = _read_remote_version()

        if local_v == remote_v:
            return  # 업데이트 없음

        if log_print:
            print(f"[Updater] 업데이트 감지: local={local_v}, remote={remote_v}")

        # 임시 폴더에서 zip 처리
        with tempfile.TemporaryDirectory(prefix="upd_", dir=str(base)) as td:
            tdir = Path(td)
            zip_path = tdir / "latest.zip"
            extract_dir = tdir / "extracted"

            _download_zip(zip_path)
            _safe_extract(zip_path, extract_dir)

            new_exe = _pick_new_exe(extract_dir, cur_exe.name)

            # version.txt는 선택(있으면 같이 교체)
            new_ver_txt = extract_dir / "version.txt"
            if not new_ver_txt.exists():
                new_ver_txt = None

            # ✅ bat 실행 시점에 임시폴더가 사라지면 안 되므로,
            # base 폴더로 "스테이징(복사)" 해둠
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

        # 배치 실행 후 종료
        subprocess.Popen(["cmd", "/c", str(base / "update.bat")], cwd=str(base))
        raise SystemExit(0)

    except SystemExit:
        raise
    except Exception as e:
        # 실패하면 그냥 계속 실행
        if log_print:
            print("[Updater] 업데이트 실패(무시하고 계속 실행):", e)
        return

# 변경사항
# 로그인 접속 아이디 리스트
login_dict = {"" : ""}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "서이추프로그램(영구제).ui"

class secondThread(QThread):
    start_signal = pyqtSignal(str)
    update = pyqtSignal(str)

    def __init__(self, input_id, input_pw, input_keyword, input_add, input_board, input_speed_n, input_comment, input_add_comment):
        super().__init__()
        self.input_id = input_id
        self.input_pw = input_pw
        self.input_keyword = input_keyword
        self.input_add = input_add
        self.input_board = input_board
        self.input_speed_n = input_speed_n
        self.input_comment = input_comment
        self.input_add_comment = input_add_comment

        
    def run(self):
        self.start_signal.emit("")
        self.update.emit("로그인 진행중...")
        self.login(self.input_id, self.input_pw)
        self.update.emit("자동화 진행중...")
        self.neighbor_add(self.input_keyword, self.input_add, self.input_board, self.input_speed_n, self.input_comment, self.input_add_comment, self.input_id)


# 이웃수, 공감, 댓글 싸그리
    def neighbor_add(self, input_keyword, n, input_board, input_speed_n, input_comment, input_add_comment, input_id):
        
        try:

            # 현재까지 완료한 서이추 수
            neighbor_index = 0


            # 현재까지 완료한 댓글 수
            comment_index = 0

            cnt = n // len(input_keyword)


            

            # ================================== 이웃추가 과정 ===========================================

            # current_N 변수에 하나씩 N만큼 이웃추가 반복

            for keyword in input_keyword:

                url = f"https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&query={keyword}&sm=tab_opt&nso=so%3Add%2Cp%3Aall"
                self.driver.get(url)
                
                # 블로그 리스트의 사용할 인덱스
                i = 0

                # 평균만큼 실행할 인덱스
                avg = 0

                # 키워드 리스트의 평균만큼 진행
                while avg < cnt:
                    time.sleep(1)

                    print(f"i : {i}, cnt : {cnt}")
                    
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")

                    print(blog_list)

                    time.sleep(1)

                    print(f"블로그 리스트 : {len(blog_list)}, 이웃 인덱스 : {neighbor_index}")

                    try:
                        # 블로그 아이디 클릭
                        # 현재 블로그 글 번호에 맞는 아이디 찾기
                        blog = blog_list[i]
                        blog.send_keys(Keys.END)
                    except:
                        self.update.emit("더 이상 해당 키워드에 블로그가 없습니다.")
                        break

                    # 새창으로 열기
                    blog.send_keys(Keys.CONTROL + "\n")
                    time.sleep(2)
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")

                    # 새창으로 드라이버 전환
                    tabs = self.driver.window_handles
                    self.driver.switch_to.window(tabs[1])

                    current_blog_url = self.driver.current_url
                
                    try:
                        print("이웃추가 try")
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        print("정렬 변환")
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        print("이웃추가 버튼 찾는중")
                        self.driver.find_element(By.CSS_SELECTOR,".add_buddy_btn__l5P_e")
                        print("댓글 버튼 찾는중")
                        self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__TUucZ")
                        print("탐색 완료")

                        self.driver.find_element(By.CSS_SELECTOR,".add_buddy_btn__l5P_e").send_keys(Keys.ENTER)
                        time.sleep(1)

                        # 이웃 수가 5000명 초과 경우
                        try:
                            over_neighbor = self.driver.find_element(By.CSS_SELECTOR, ".desc__LlxVe").text
                            print(over_neighbor)
                            print("5,000" in over_neighbor)
                            if "5,000" in over_neighbor:
                                self.manage_over_neighbor(input_id)
                                time.sleep(1)

                                print("5000명 초과 작업 끝")

                                self.driver.close()
                                tabs = self.driver.window_handles
                                self.driver.switch_to.window(tabs[0])

                                self.update.emit("서이추 작업을 재개합니다.")
                                continue
                        except:
                            print("except")
                            pass
                        
                        
                        # 서로 이웃 추가 버튼 클릭
                        self.driver.find_element(By.CSS_SELECTOR,"#bothBuddyRadio").click()
                        time.sleep(1)



                    except:
                        self.update.emit("\n서이추 또는 댓글 버튼이 없어 다음으로 넘어갑니다.\n")
                        i += 1

                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        continue

                    else:
                        
                        try:
                            # 멘트 남기기
                            text_area = self.driver.find_element(By.CSS_SELECTOR,"#buddyAddForm > fieldset > div > div.set_detail_t1 > div.set_detail_t1 > div > textarea")
                            text_area.click()
                            text_area.send_keys(Keys.CONTROL, "a")
                            text_area.send_keys(Keys.DELETE)
                            text_area.send_keys(f"{input_board[random.randint(0, len(input_board) - 1)]}")

                        except:
                            self.update.emit("\n서로이웃신청이 불가하여 다음으로 넘어갑니다.\n")
                            i += 1

                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue

                        # 그룹 선택
                        groups = self.driver.find_elements(By.CSS_SELECTOR, "#buddyGroupSelect > option")
                        group_idx = 0
                        group_err = 0

                        while group_idx < len(groups):
                            
                            try:
                                groups[group_idx].click()
                                time.sleep(1)

                            except:
                                print("그룹 선택에 오류가 발생했습니다.")
                                self.update.emit("그룹 선택에 오류가 발생했습니다.")
                                self.update.emit(f"groups = {len(groups)}, group_idx = {group_idx}, group_err = {group_err}")
                                self.update.emit("재시도 합니다.")
                                print(groups, group_idx, group_err)
                                continue

                            # 이웃초과가 한번 떴을 경우
                            if group_err > 0:
                                self.driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)

                                over_alert = self.driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

                                # 이웃초과할 경우, 다시 while문 돈다.
                                if len(over_alert) > 0:
                                    over_alert[0].click()
                                    group_idx += 1
                                    group_err += 1
                                    continue

                                # 정상 이웃추가 되었을 경우
                                else:
                                    break


                            # 처음 시도인 경우
                            else:

                                # 확인 
                                time.sleep(input_speed_n)
                                self.driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)
                                
                                
                                over_alert = self.driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

                                print(len(over_alert), over_alert)

                                # 이웃초과할 경우, 다시 while문 돈다.
                                if len(over_alert) > 0:
                                    over_alert[0].click()
                                    group_idx += 1
                                    group_err += 1
                                    continue                                

                                # 이웃초과가 아닐 경우
                                else:
                                    break

                        
                        if group_idx == len(groups):
                            self.update.emit("이웃그룹의 정원이 모두 찼습니다.")
                            self.update.emit("프로그램을 종료합니다.")
                            break

                        else:
                            neighbor_index += 1

            
                        # 이웃추가 완료 문구 띄우기
                        self.update.emit(f"\n이웃추가 {neighbor_index}개 완료!")

                        self.driver.get(current_blog_url)
                        time.sleep(1)
                        
                        # 블로그 정렬 바꾸기
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__TUucZ")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.ENTER)
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            time.sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.update.emit(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            comment_index += 1
                            time.sleep(2)
                            

                        else:
                            print("댓글 pass")
                            pass


                    print("탭을 닫습니다.")
                    # 현재 탭 닫기
                    self.driver.close()
                    self.driver.switch_to.window(tabs[0])
                    i += 1
                    avg += 1


                self.update.emit("다음 키워드로 넘어갑니다.\n")

    ###################### 1차 작업 끝 ###################################

            # 아직 목표 서이추 수를 도달하지 못한 경우
            if neighbor_index < n:
                print("목표 서이추 수 미도달")
                self.update.emit("키워드가 없어 현재 키워드로 진행합니다.\n")

                while neighbor_index < n:

                    print(f"neighbor_index : {neighbor_index}, n : {n}")

                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")
                    print(f"블로그 리스트 길이 : {len(blog_list)}, i : {i}")
                    
                    try:
                        # 블로그 아이디 클릭
                        # 현재 블로그 글 번호에 맞는 아이디 찾기
                        blog = blog_list[i]
                        blog.send_keys(Keys.PAGE_DOWN)
                    except:
                        self.update.emit("인덱스 아웃 오브 레인지")
                        break

                    # 새창으로 열기
                    blog.send_keys(Keys.CONTROL + "\n")
                    time.sleep(2)
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")

                    # 새창으로 드라이버 전환
                    tabs = self.driver.window_handles
                    self.driver.switch_to.window(tabs[1])

                    current_blog_url = self.driver.current_url
                
                    try:
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        self.driver.find_element(By.CSS_SELECTOR,".add_buddy_btn__l5P_e")
                        self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__TUucZ")

                        self.driver.find_element(By.CSS_SELECTOR,".add_buddy_btn__l5P_e").send_keys(Keys.ENTER)
                        time.sleep(1)
                        
                        # 서로 이웃 추가 버튼 클릭
                        self.driver.find_element(By.CSS_SELECTOR,"#bothBuddyRadio").click()

                    except:
                        self.update.emit("\n서이추 버튼이 없어 다음으로 넘어갑니다.\n")
                        i += 1

                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        continue

                    else:

                        try:
                            # 멘트 남기기
                            text_area = self.driver.find_element(By.CSS_SELECTOR,"#buddyAddForm > fieldset > div > div.set_detail_t1 > div.set_detail_t1 > div > textarea")
                            text_area.click()
                            text_area.send_keys(Keys.CONTROL, "a")
                            text_area.send_keys(Keys.DELETE)
                            text_area.send_keys(f"{input_board[random.randint(0, len(input_board) - 1)]}")

                        except:
                            self.update.emit("\n서로이웃신청이 불가하여 다음으로 넘어갑니다.\n")
                            i += 1

                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue

                        # 그룹 선택
                        groups = self.driver.find_elements(By.CSS_SELECTOR, "#buddyGroupSelect > option")
                        group_idx = 0
                        group_err = 0

                        while group_idx < len(groups):
                            
                            try:
                                groups[group_idx].click()
                                time.sleep(1)
                            except:
                                print("그룹 선택에 오류가 발생했습니다.")
                                self.update.emit("그룹 선택에 오류가 발생했습니다.")
                                self.update.emit(f"groups = {len(groups)}, group_idx = {group_idx}, group_err = {group_err}")
                                self.update.emit("재시도 합니다.")
                                print(groups, group_idx, group_err)
                                continue

                            # 이웃초과가 한번 떴을 경우
                            if group_err > 0:
                                self.driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)

                                over_alert = self.driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

                                # 이웃초과할 경우, 다시 while문 돈다.
                                if len(over_alert) > 0:
                                    over_alert[0].click()
                                    group_idx += 1
                                    group_err += 1
                                    continue

                                # 정상 이웃추가 되었을 경우
                                else:
                                    break


                            # 처음 시도인 경우
                            else:

                                # 확인 
                                time.sleep(input_speed_n)
                                self.driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)
                                
                                
                                over_alert = self.driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

                                print(len(over_alert), over_alert)

                                # 이웃초과할 경우, 다시 while문 돈다.
                                if len(over_alert) > 0:
                                    over_alert[0].click()
                                    group_idx += 1
                                    group_err += 1
                                    continue                                

                                # 이웃초과가 아닐 경우
                                else:
                                    break

                        
                        if group_idx == len(groups):
                            self.update.emit("이웃그룹의 정원이 모두 찼습니다.")
                            self.update.emit("프로그램을 종료합니다.")
                            break

                        else:
                            neighbor_index += 1

            
                        # 이웃추가 완료 문구 띄우기
                        self.update.emit(f"\n이웃추가 {neighbor_index}개 완료!")

                        self.driver.get(current_blog_url)
                        time.sleep(1)

                        # 블로그 정렬 바꾸기
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__TUucZ")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.ENTER)
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            time.sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.update.emit(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            comment_index += 1
                            time.sleep(2)


                        else:
                            print("댓글 pass")
                            pass


                        # 완료된 작업 실시간 반영
                        self.update.emit("\n")

                    print("탭을 닫습니다.")
                    # 현재 탭 닫기
                    self.driver.close()
                    self.driver.switch_to.window(tabs[0])
                    i += 1


            # 아직 댓글이 남아 있는 경우
            if comment_index < input_add_comment:
                self.update.emit("\n남은 댓글 작업을 시작합니다.\n")

                current_url = self.driver.current_url

                # like_index와 comment_index가 입력해놓은 숫자가 될 때까지 반복
                while comment_index != input_add_comment:

                    # 서이추가 0인 경우
                    if current_url == "data:,":
                        pass
                    
                    # 서이추 횟수까지는 모두 채운 경우
                    else:
                        blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")

                        try:
                            # 블로그 아이디 클릭
                            # 현재 블로그 글 번호에 맞는 아이디 찾기
                            blog = blog_list[i]
                            blog.send_keys(Keys.END)
                        except:
                            self.update.emit("인덱스 아웃 오브 레인지")
                            break

                        # 새창으로 열기
                        blog.send_keys(Keys.CONTROL + "\n")
                        time.sleep(2)
                        blog_list = self.driver.find_elements(By.CSS_SELECTOR, "a.fender-ui_475445f0")

                        # 새창으로 드라이버 전환
                        tabs = self.driver.window_handles
                        self.driver.switch_to.window(tabs[1])

                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__TUucZ").send_keys(Keys.ENTER)
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            time.sleep(2)
                            self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.update.emit(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            comment_index += 1
                            time.sleep(2)
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])

                        else:
                            print("댓글 pass")
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            pass

                        # 완료된 작업 실시간 반영
                        self.update.emit("\n")

                        i += 1

            self.update.emit("\n모든 서이추 및 댓글 작업 완료!")
            return 
        except:
            traceback_message = str(traceback.format_exc())
            self.update.emit(traceback_message)
            self.update.emit("\n* 오류가 발생했습니다.")

    def login(self, input_id, input_pw):

            # 크롬창 생성
            self.driver = webdriver.Chrome()

            # 웹페이지 해당 주소 이동
            self.driver.implicitly_wait(5)
            self.driver.maximize_window()
            self.driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")

            time.sleep(3)

            # 아이디 입력
            id = self.driver.find_element(By.CSS_SELECTOR, "#id")
            id.click()
            pyperclip.copy(input_id)
            pyautogui.hotkey("ctrl", "v")


            # 비밀번호 입력
            pw = self.driver.find_element(By.CSS_SELECTOR, "#pw")
            pw.click()
            pyperclip.copy(input_pw)
            pyautogui.hotkey("ctrl", "v")


            # 로그인 버튼
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "#log\.login")
            login_btn.click()

            # 로그인 브라우저 등록
            try:
                self.driver.find_element(By.CSS_SELECTOR, "#new\.save").click()
            except:
                pass


            # 로그인 완료
            # 로그인 성공 시 드라이버 반환
            # 로그인 실패 시 드라이버 종료 후  0 반환

            check = self.driver.find_elements(By.CSS_SELECTOR, ".MyView-module__my_info___GNmHz")

            # 로그인 성공
            if len(check) > 0:
                self.update.emit("로그인 성공")
            
            # 로그인 실패
            else:
                self.driver.close()
                self.update.emit("로그인 실패")


    def manage_over_neighbor(self, input_id):
        
        self.update.emit("\n이웃 수가 5000명이 넘어 이웃관리로 넘어갑니다.\n")

        try:
            self.driver.get(f"https://admin.blog.naver.com/{input_id}")
            time.sleep(2)

            self.driver.find_element(By.CSS_SELECTOR, "#buddyinvite_config_anchor").click()
            print("서로이웃 신청 메뉴 클릭")

            time.sleep(2)

            self.driver.switch_to.frame("papermain")

            # 보낸신청 메뉴 클릭
            self.driver.find_element(By.CSS_SELECTOR, "#inviteMe > ul > li._nclk\(bas_neitadd\.send\) > a").click()

            try:
                # 신청일 리스트
                dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
            except:
                print("보낸 신청이 없습니다.")
                self.update.emit("보낸 신청이 없습니다.")
                return self.driver
                

            # date의 text를 담아두는 리스트
            date_list = []

            for i in range(len(dates)):
                date_list.append(dates[i].text.replace(".", "-")[:-1])

            # 신청한 사람 리스트
            users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

            # 신청취소 버튼 리스트
            cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

            current_date_time = datetime.now()

            # 2주(14일) 전의 날짜 계산
            two_weeks_ago = current_date_time - timedelta(days=14)

            # 날짜 형식화 (예: YYYY-MM-DD)
            two_weeks_ago = two_weeks_ago.strftime("%Y-%m-%d")[2:]

            # 6개월 전 날짜 계산
            six_months_ago = current_date_time - timedelta(days=180)
            six_months_ago = six_months_ago.strftime("%Y-%m-%d")[2:]

            a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
            a_index = 0

            ########################### 다음 페이지들이 있는 경우 ###########################
            if len(a) > 0:

                while 1:
                    
                    self.update.emit("\n다음 페이지로\n")

                    try:
                        # 신청일 리스트
                        dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                    except:
                        print("보낸 신청이 없습니다.")
                        self.update.emit("보낸 신청이 없습니다.")
                        return
                    

                    # date의 text를 담아두는 리스트
                    date_list = []

                    for index in range(len(dates)):
                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                    # 신청한 사람 리스트
                    users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                    # 신청취소 버튼 리스트
                    cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                    i = 0

                    while i != len(dates) or i < len(dates):

                        print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                        self.update.emit(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}")
                        
                        # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                        if date_list[i] <= two_weeks_ago:
                            print("2주 이상 지남 -> 삭제 대상")
                            self.update.emit("2주 이상 지남 -> 삭제 대상\n")

                            t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = self.driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                print("1페이지가 아님")
                                time.sleep(1.5)
                                a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                a[a_index-1].click()
                                time.sleep(1.5)


                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue
                            


                        # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                        else:
                            # 블로그 6개월 활동 확인
                            users[i].click()

                            tabs = self.driver.window_handles
                            self.driver.switch_to.window(tabs[2])
                            time.sleep(1)
                            url = self.driver.current_url

                            # url 모바일로 변경
                            url = url[:8] + "m." + url[8:]

                            self.driver.get(url)
                            time.sleep(4)

                            try:
                                # 블로그 정렬 바꾸기
                                self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                                time.sleep(1)
                            
                            except:
                                print("비정상 블로그 -> 삭제")
                                self.update.emit("비정상 블로그 -> 삭제\n")

                                self.driver.close()
                                self.driver.switch_to.window(tabs[1])

                                self.driver.switch_to.frame("papermain")

                                t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                                
                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = self.driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue


                            # 블로그 최신글 날짜 추출
                            try:
                                blog_time = self.driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.update.emit(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")

                            except:
                                self.update.emit("게시물이 없는 블로그 -> 유지")
                                self.driver.close()
                                self.driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                self.driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                            # 먼저 hh시간전, mm분인 블로그 색출
                            if "시간" in blog_time or "분" in blog_time:
                                print("hh시간전, mm분인 블로그 -> 유지")
                                self.update.emit("hh시간전, mm분인 블로그 -> 유지\n")

                                self.driver.close()
                                self.driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                self.driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            
                            # 6개월전 블로그 색출
                            else:

                                blog_time = blog_time.replace(". ", "-")[2 : -1]

                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.update.emit(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")

                                # 최신글이 6개월 이상 된 경우
                                if blog_time < six_months_ago:
                                    print("6개월 이상됨 -> 삭제 대상")
                                    self.update.emit("6개월 이상됨 -> 삭제 대상\n")

                                    self.driver.close()
                                    self.driver.switch_to.window(tabs[1])
                                    time.sleep(2)

                                    self.driver.switch_to.frame("papermain")

                                    # 현재 페이지 저장
                                    t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                    time.sleep(2)
                                    # 신청 취소
                                    cancels[i].click()
                                    time.sleep(2)

                                    # 경고창 확인
                                    result = self.driver.switch_to.alert
                                    result.accept()
                                    result.dismiss()

                                    self.driver.switch_to.window(tabs[1])
                                    time.sleep(0.5)
                                    self.driver.switch_to.frame("papermain")

                                    # 현재 페이지로 회귀
                                    if t > 1:
                                        print("1페이지가 아님")
                                        time.sleep(1.5)
                                        a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                        a[a_index-1].click()
                                        time.sleep(1.5)

                                    # 요소들 새로고침
                                    # 신청일 리스트
                                    dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                                    # date의 text를 담아두는 리스트
                                    date_list = []

                                    for index in range(len(dates)):
                                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                                    # 신청한 사람 리스트
                                    users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                    # 신청취소 버튼 리스트
                                    cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                    continue

                                # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                                else:
                                    print("활동중인 블로그 -> 유지")
                                    self.update.emit("활동중인 블로그 -> 유지\n")

                                    self.driver.close()
                                    self.driver.switch_to.window(tabs[1])
                                    time.sleep(2)
                                    self.driver.switch_to.frame("papermain")
                                    i += 1
                                    continue

                    # 다음 페이지들의 리스트
                    a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")

                    try:
                        a[a_index].click()
                        time.sleep(2)
                        a_index += 1
                        continue

                    except:
                        print("페이지 끝")
                        self.update.emit("\n페이지 끝\n")
                        self.update.emit("이웃관리 완료!")
                        return
                        


                    


            ########################### 현재 페이지가 끝인 경우 ########################
            else:
                print("현재 페이지가 마지막입니다.")
                self.update.emit("현재 페이지가 마지막입니다.")

                try:
                    # 신청일 리스트
                    dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                except:
                    print("보낸 신청이 없습니다.")
                    self.update.emit("보낸신청이 없습니다.")
                    self.update.emit("\n모든 이웃관리 완료!\n")
                    return
                    
                

                # date의 text를 담아두는 리스트
                date_list = []

                for index in range(len(dates)):
                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                # 신청한 사람 리스트
                users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                # 신청취소 버튼 리스트
                cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                i = 0

                while i != len(dates) or i < len(dates):

                    print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                    self.update.emit(f"\nuser : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}\n")

                    # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                    if date_list[i] <= two_weeks_ago:
                        print("2주 이상 지남 -> 삭제 대상")
                        self.update.emit("2주 이상 지남 -> 삭제 대상\n")

                        t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                        time.sleep(2)
                        # 신청 취소
                        cancels[i].click()
                        time.sleep(2)

                        # 경고창 확인
                        result = self.driver.switch_to.alert
                        result.accept()
                        result.dismiss()

                        # 현재 페이지로 회귀
                        if t > 1:
                            print("1페이지가 아님")
                            time.sleep(1.5)
                            a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                            a[a_index-1].click()
                            time.sleep(1.5)
                            

                        # 요소들 새로고침
                        # 신청일 리스트
                        dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                        # date의 text를 담아두는 리스트
                        date_list = []

                        for index in range(len(dates)):
                            date_list.append(dates[index].text.replace(".", "-")[:-1])

                        # 신청한 사람 리스트
                        users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                        # 신청취소 버튼 리스트
                        cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                        continue
                        


                    # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                    else:
                        # 블로그 6개월 활동 확인
                        users[i].click()

                        tabs = self.driver.window_handles
                        self.driver.switch_to.window(tabs[2])
                        time.sleep(1)
                        url = self.driver.current_url

                        # url 모바일로 변경
                        url = url[:8] + "m." + url[8:]

                        self.driver.get(url)
                        time.sleep(4)

                        try:
                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__XQnk9 > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                            time.sleep(1)
                        
                        except:
                            print("비정상 블로그 -> 삭제")
                            self.update.emit("비정상 블로그 -> 삭제\n")

                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])

                            self.driver.switch_to.frame("papermain")

                            t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                            
                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = self.driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                time.sleep(1.5)
                                a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                print("1페이지가 아님")
                                a[a_index-1].click()
                                time.sleep(1.5)

                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue


                        # 블로그 최신글 날짜 추출
                        try:
                            blog_time = self.driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                            print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                            self.update.emit(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")

                        except:
                            self.update.emit("게시물이 없는 블로그 -> 유지")

                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])
                            time.sleep(2)
                            self.driver.switch_to.frame("papermain")
                            i += 1
                            continue

                        # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                        # 먼저 hh시간전, mm분인 블로그 색출
                        if "시간" in blog_time or "분" in blog_time:
                            print("hh시간전, mm분인 블로그 -> 유지")
                            self.update.emit("hh시간전, mm분인 블로그 -> 유지\n")

                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])
                            time.sleep(2)
                            self.driver.switch_to.frame("papermain")
                            i += 1
                            continue


                        
                        # 6개월전 블로그 색출
                        else:

                            blog_time = blog_time.replace(". ", "-")[2 : -1]

                            # 최신글이 6개월 이상 된 경우
                            if blog_time < six_months_ago:
                                print("6개월 이상됨 -> 삭제 대상")
                                self.update.emit("6개월 이상됨 -> 삭제 대상\n")

                                self.driver.close()
                                self.driver.switch_to.window(tabs[1])
                                time.sleep(2)

                                t = int(self.driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = self.driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                self.driver.switch_to.window(tabs[1])
                                time.sleep(0.5)
                                self.driver.switch_to.frame("papermain")

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = self.driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = self.driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = self.driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = self.driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue

                            # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                            else:
                                print("활동중인 블로그 -> 유지")
                                self.update.emit("활동중인 블로그 -> 유지\n")

                                self.driver.close()
                                self.driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                self.driver.switch_to.frame("papermain")
                                i += 1
                                continue
                
                self.update.emit("\n이웃관리 완료!\n")
                return

        except:
            traceback_message = str(traceback.format_exc())
            self.update.emit(traceback_message)
            self.update.emit("\n* 오류가 발생했습니다.")


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
        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH2), self)

        # 실행 버튼 클릭 이벤트
        self.start_btn.clicked.connect(self.main)
        
        # 종료 버튼 클릭 이벤트
        self.exit_btn.clicked.connect(self.close)

        # 리셋 버튼 클릭 이벤트
        self.reset_btn.clicked.connect(self.reset)

        # 중지 버튼 클릭 이벤트
        self.stop_btn.clicked.connect(self.stop)

        # 이전 세팅값 불러오기
        settings = QSettings("블로그1", "서이추프로그램3")
        self.id.setText(settings.value("id", ""))
        self.pw.setText(settings.value("pw", ""))

        self.search_keyword.setText(settings.value("keyword", ""))
        self.add_n.setValue(settings.value("add", 0, type=int))
        self.add_comment.setValue(settings.value("add_comment", 0, type=int))

        self.board.setText(settings.value("board", "이웃신청멘트를 입력하세요."))
        self.comment.setText(settings.value("comment", "댓글을 입력하세요."))

        self.speed_n.setValue(settings.value("speed_n", 0, type=int))
        self.speed_comment.setValue(settings.value("speed_comment", 0, type=int))

    def update_text_browser(self, string):
        self.textBrowser.append(f"{string}")




    # 실행 버튼 함수
    def main(self):

        # 입력 받은 것들 가져오기
        input_id = self.id.text()
        input_pw = self.pw.text()
        input_keyword = self.search_keyword.text()
        input_add = self.add_n.value()

        # 이웃신청 멘트 랜덤
        input_board = self.board.toPlainText()

        # 댓글 멘트 랜덤
        input_comment = self.comment.toPlainText()


        print(input_board, input_comment)

        input_speed_n = self.speed_n.value()
        input_add_comment = self.add_comment.value()

        # 유효성 검사
        if input_id == "" or input_pw == "" or input_keyword == ""  or input_board == "이웃신청멘트를 입력하세요." or input_comment == '댓글을 입력하세요.':
            self.textBrowser.setText("빈칸을 모두 채워주세요.")
            return 0
        
        # 세팅값 저장하기
        settings = QSettings("블로그1", "서이추프로그램3")
        settings.setValue("id", input_id)
        settings.setValue("pw", input_pw)
        settings.setValue("keyword", input_keyword)
        settings.setValue("add", input_add)
        settings.setValue("add_comment", input_add_comment)
        settings.setValue("speed_n", input_speed_n)
        settings.setValue("board", input_board)
        settings.setValue("comment", input_comment)


        self.textBrowser.setText("")
        QApplication.processEvents()

        # 세팅값 저장 때문에 뒤늦게 처리
        input_keyword = self.search_keyword.text().split(',')

        # 이웃신청멘트 값 리스트로 전환 후 랜덤
        input_board = input_board.split("\n")
        random.shuffle(input_board)

        # 댓글 값 리스트 전환 후 랜덤
        input_comment = input_comment.split("\n")
        random.shuffle(input_comment)

        self.second_thread = secondThread(input_id, input_pw, input_keyword, input_add, input_board, input_speed_n, input_comment, input_add_comment)
        self.second_thread.update.connect(self.update_text_browser)

        self.second_thread.start_signal.connect(self.update_start_signal)

        # Thread 실행
        self.second_thread.start()
        
            
    def update_start_signal(self, signal):
        self.textBrowser.append(f"{signal}")

#===============================================================================================================

    def stop(self):
        self.second_thread.terminate()
        self.textBrowser.append("\n*프로그램 중지*\n")
    

#=============================================================================================================


            
    
    # 리셋 버튼 함수
    def reset(self):
        self.id.setText("")
        self.pw.setText("")
        self.search_keyword.setText("")
        self.add_n.clear()
        self.board.setText("이웃신청멘트를 입력하세요.")
        self.textBrowser.setText("")
        self.comment.setText("댓글을 입력하세요.")
        

    # 종료 버튼 함수
    def close(self):
        sys.exit()
        
# ✅ GUI 띄우기 전에 1번만 업데이트 체크
check_and_apply_update_or_continue()

QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = first()
main_dialog.show()

sys.exit(app.exec_())
