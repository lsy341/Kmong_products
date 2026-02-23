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

from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#ActionChains모듈 가져오기
from selenium.webdriver import ActionChains


# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())

# pyqt 부분
import os

# 변경사항
# 로그인 접속 아이디 리스트
login_dict = {"wkrdjqdyd1" : "akzpxld1!"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "이웃새글.ui"

class secondThread(QThread):
    start_signal = pyqtSignal(str)
    update = pyqtSignal(str)

    def __init__(self, reserveTimes, input_process, input_id, input_pw, input_keyword, input_add, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_add_like2, input_add_comment2, input_comment2, input_speed_comment, first_delay, last_delay, blog_nickname):
        super().__init__()
        self.input_id = input_id
        self.input_pw = input_pw
        self.input_keyword = input_keyword
        self.input_add = input_add
        self.input_board = input_board
        self.input_speed_n = input_speed_n
        self.input_like = input_like
        self.input_comment = input_comment
        self.input_add_comment = input_add_comment
        self.input_speed_like = input_speed_like
        self.input_speed_comment = input_speed_comment

        self.input_process = input_process
        self.input_add_like2 = input_add_like2
        self.input_add_comment2 = input_add_comment2
        self.input_comment2 = input_comment2
        
        self.reserveTimes = reserveTimes

        self.first_delay = first_delay
        self.last_delay = last_delay

        self.blog_nickname = blog_nickname
        

        
    def run(self):
        try:
            self.start_signal.emit("")

            self.update.emit("예약 시간까지 대기중...")

            time_index = 0

            if self.reserveTimes == 0:
                self.update.emit("로그인 진행중...")
                check = self.login(self.input_id, self.input_pw)
                self.update.emit("자동화 진행중...")
                if self.input_process == 1:
                    self.neighbor_add(self.input_keyword, self.input_add, self.input_board, self.input_speed_n, self.input_like, self.input_comment, self.input_add_comment, self.input_speed_like, self.input_id)
                else:
                    self.my_neighbor(self.input_add_like2, self.input_add_comment2, self.input_comment2, self.input_speed_like, self.input_speed_comment, self.first_delay, self.last_delay, self.blog_nickname)
                
                return 
                
            else:
                while True:

                    for reservetime in self.reserveTimes:

                        while True:

                            # 현재 시간 불러오기
                            current_time = datetime.now().strftime("%H:%M")

                            if current_time == reservetime:
                                self.update.emit("로그인 진행중...")
                                check = self.login(self.input_id, self.input_pw)

                                if check == 0:
                                    return

                                self.update.emit("자동화 진행중...")

                                if self.input_process == 1:
                                    self.neighbor_add(self.input_keyword, self.input_add, self.input_board, self.input_speed_n, self.input_like, self.input_comment, self.input_add_comment, self.input_speed_like, self.input_id)
                                else:
                                    self.my_neighbor(self.input_add_like2, self.input_add_comment2, self.input_comment2, self.input_speed_like, self.input_speed_comment, self.first_delay, self.last_delay, self.blog_nickname)
                                break

                            else:
                                continue

                        time_index += 1

                        if time_index == len(self.reserveTimes):
                            time_index = 0

                        self.update.emit("\n다음 예약 시간까지 대기중...")
                        self.update.emit(f"다음 예약 시간 : {self.reserveTimes[time_index]}\n")
                        time.sleep(10)

        except:
            traceback_message = str(traceback.format_exc())
            self.update.emit(traceback_message)
            self.update.emit("\n* 오류가 발생했습니다.")


    def my_neighbor(self, input_add_like2, input_add_comment2, input_comment2, input_speed_like, input_speed_comment, first_delay, last_delay, blog_nickname):

        try:

            action = ActionChains(self.driver)

            # 현재까지 완료한 공감 수
            like_index = 0

            # 현재까지 완료한 댓글 수
            comment_index = 0  

            # 아직 좋아요와 댓글이 남아 있는 경우
            if like_index < input_add_like2 or comment_index < input_add_comment2:
                self.update.emit("\n이웃새글 작업을 시작합니다.\n")

                self.driver.get("https://m.blog.naver.com/FeedList.naver")

                likes_btn_index = 0
                comment_btn_index = 0
                is_like_empty = 0

                # like_index와 comment_index가 입력해놓은 숫자가 될 때까지 반복
                while like_index != input_add_like2 or comment_index != input_add_comment2:

                    delay = random.randint(first_delay * 60, last_delay * 60)
                    print(f"{delay}초 기다릴거임")

                    self.update.emit(f"{delay}초 딜레이 중...\n")

                    time.sleep(delay)

                    try:
                        # 웹 드라이버가 최대 5초간 Alert를 기다림
                        WebDriverWait(self.driver, 5).until(EC.alert_is_present())

                        # Alert 창에 접근
                        alert = self.driver.switch_to.alert

                        # 필요한 경우, 여기서 Alert 창을 닫거나 다른 조치를 취할 수 있습니다.
                        alert.accept()  # 또는 alert.dismiss()

                        time.sleep(1)

                        self.update.emit("\n경고창이 떠 페이지를 새로고침 합니다.\n")
                        
                        current_url = self.driver.current_url
                        self.driver.get(current_url)

                        time.sleep(2)

                        scroll_count = (like_index + comment_index) // 2 + 1

                        self.update.emit("스크롤 하여 이전 작업을 다시 진행합니다")

                        for i in range(scroll_count // 10 + 1):
                            post_title = self.driver.find_elements(By.CSS_SELECTOR, ".title__tl7L1.ell2")
                            action.move_to_element(post_title[-1]).perform()
                            time.sleep(2)
                        

                        continue


                    except (TimeoutException, NoAlertPresentException):
                        # Alert가 나타나지 않았거나, 이미 사라졌을 경우

                        try:

                            likes_btn = self.driver.find_elements(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                            print(likes_btn)
                            comment_btn = self.driver.find_elements(By.CSS_SELECTOR, ".comment_btn__lcx93")

                            post_title = self.driver.find_elements(By.CSS_SELECTOR, ".title__tl7L1.ell2")
                                
                            # 좋아요
                            # 좋아요를 눌러야하는 경우
                            if like_index < input_add_like2:
                                try:
                                    likes_btn = self.driver.find_elements(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                                    print(likes_btn)
                                    comment_btn = self.driver.find_elements(By.CSS_SELECTOR, ".comment_btn__lcx93")
                                    time.sleep(1)
                                    time.sleep(input_speed_like)

                                    # 좋아요 누르기
                                    likes_btn[likes_btn_index].send_keys(Keys.ENTER)


                                except:
                                    self.update.emit("좋아요 버튼을 찾을 수 없습니다")
                                    is_like_empty += 1

                                    action.move_to_element(post_title[-1]).perform()
                                    time.sleep(2)

                                    self.update.emit("좋아요 버튼을 찾을 수 없어 스크롤을 내려 블로그 리스트를 새로 불러옵니다.\n")

                                    for i in range(5):
                                        post_title = self.driver.find_elements(By.CSS_SELECTOR, ".title__tl7L1.ell2")
                                        action.move_to_element(post_title[-1]).perform()
                                        time.sleep(2)

                                else:
                                    like_index += 1
                                    is_like_empty = 0
                                    self.update.emit(f"좋아요 {like_index}개 성공!")

                                # 더 이상 좋아요를 찾을 수 없음
                                if is_like_empty == 2:
                                    like_index = input_add_like2
                                    self.update.emit("스크롤을 내려도 좋아요 버튼을 찾을 수 없어 좋아요 기능을 마칩니다.\n\n")
                                    is_like_empty = 0                            
                                    
                                
                                time.sleep(2)

                            #=======================댓글 작업==========================

                            print(f"댓글 : {comment_index}, {input_add_comment2}")

                            #  댓글을 입력해야 하는 경우
                            if comment_index < input_add_comment2:

                                time.sleep(1)
                                try:

                                    likes_btn = self.driver.find_elements(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                                    print(likes_btn)
                                    comment_btn = self.driver.find_elements(By.CSS_SELECTOR, ".comment_btn__lcx93")
                                    
                                    # 새창으로 열기
                                    comment_btn[comment_btn_index].send_keys(Keys.CONTROL + "\n")
                                    time.sleep(1) 

                                except:
                                    self.update.emit("\n게시물에 댓글을 막아두어 스크롤 합니다. \n")
                                    time.sleep(1)

                                    comment_btn = self.driver.find_elements(By.CSS_SELECTOR, ".comment_btn__lcx93")

                                    for i in range(5):
                                        post_title = self.driver.find_elements(By.CSS_SELECTOR, ".title__tl7L1.ell2")
                                        action.move_to_element(post_title[-1]).perform()
                                        time.sleep(2)

                                    continue


                                else:

                                    # 새창으로 드라이버 전환
                                    tabs = self.driver.window_handles
                                    self.driver.switch_to.window(tabs[1])

                                    time.sleep(2)

                                    # 이전에 내가 댓글을 단 적이 있는지 체크
                                    check_name = self.driver.find_elements(By.CSS_SELECTOR, ".u_cbox_nick")
                                    time.sleep(2)
                                    
                                    for cn in check_name:

                                        if cn.text == blog_nickname:
                                            comment_index = input_add_comment2
                                            self.update.emit("\n* 이전에 등록한 댓글이 있어 댓글 기능을 중단합니다. *\n")
                                            break

                                    if comment_index == input_add_comment2:
                                        self.driver.close()
                                        time.sleep(2)
                                        self.driver.switch_to.window(tabs[0])
                                        time.sleep(0.6)
                                        continue

                                    # 댓글 창 입력
                                    time.sleep(0.5)
                                    self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment2[random.randint(0, len(input_comment2) - 1)])
                                    time.sleep(input_speed_comment)
                                    self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                                    comment_index += 1
                                    comment_btn_index += 1
                                    self.update.emit(f"댓글 {comment_index}개 입력 완료!\n")
                                    time.sleep(2)
                                    self.driver.close()
                                    self.driver.switch_to.window(tabs[0])
                            print("No alert present.")

                        except UnexpectedAlertPresentException as e:
                            # 다른 예상치 못한 Alert가 나타났을 경우
                            continue


                        

            self.update.emit("\n모든 이웃새글 공감, 댓글 작업 완료!")
            self.driver.quit()
            return 0
    
        
        except:
            traceback_message = str(traceback.format_exc())
            self.update.emit(traceback_message)
            self.update.emit("\n* 오류가 발생했습니다.")






# 이웃수, 공감, 댓글 싸그리
    def neighbor_add(self, input_keyword, n, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_id):
        
        try:

            # 현재까지 완료한 서이추 수
            neighbor_index = 0

            # 현재까지 완료한 공감 수
            like_index = 0

            # 현재까지 완료한 댓글 수
            comment_index = 0

            cnt = n // len(input_keyword)


            

            # ================================== 이웃추가 과정 ===========================================

            # current_N 변수에 하나씩 N만큼 이웃추가 반복

            for keyword in input_keyword:

                url = f"https://m.search.naver.com/search.naver?where=m_blog&query={keyword}&sm=mtb_opt&nso=so%3Add%2Cp%3Aall"
                self.driver.get(url)
                
                # 블로그 리스트의 사용할 인덱스
                i = 0

                # 평균만큼 실행할 인덱스
                avg = 0

                # 키워드 리스트의 평균만큼 진행
                while avg < cnt:

                    print(f"i : {i}, cnt : {cnt}")
                    
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")

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
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")

                    # 새창으로 드라이버 전환
                    tabs = self.driver.window_handles
                    self.driver.switch_to.window(tabs[1])

                    current_blog_url = self.driver.current_url
                
                    try:
                        print("이웃추가 try")
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        self.driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                        self.driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B")
                        self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                        self.driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B").send_keys(Keys.ENTER)
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
                        self.update.emit("\n서이추 또는 좋아요, 댓글 버튼이 없어 다음으로 넘어갑니다.\n")
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
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        #===================좋아요 과정 ============================
                        
                        print(f"좋아요 : {like_index}, {input_like}")

                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            # 좋아요 누르기
                            time.sleep(input_speed_like)
                            self.driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                            like_index += 1

                            self.update.emit(f"좋아요 {like_index}개 성공!")
                            time.sleep(2)

                        # 좋아요를 모두 누른 경우
                        else:
                            print("좋아요 pass")
                            pass
                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.CONTROL + "\n")
                            tabs = self.driver.window_handles
                            self.driver.switch_to.window(tabs[2])
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.update.emit(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            comment_index += 1
                            time.sleep(2)
                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])

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

                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")
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
                    blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")

                    # 새창으로 드라이버 전환
                    tabs = self.driver.window_handles
                    self.driver.switch_to.window(tabs[1])

                    current_blog_url = self.driver.current_url
                
                    try:
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        self.driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                        self.driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B")
                        self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                        self.driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B").send_keys(Keys.ENTER)
                        time.sleep(1)
                        
                        # 서로 이웃 추가 버튼 클릭
                        self.driver.find_element(By.CSS_SELECTOR,"#bothBuddyRadio").click()

                    except:
                        self.update.emit("\n서이추 또는 좋아요 버튼이 없어 다음으로 넘어갑니다.\n")
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
                        self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        #===================좋아요 과정 ============================
                        
                        print(f"좋아요 : {like_index}, {input_like}")

                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            time.sleep(input_speed_like)
                            # 좋아요 누르기
                            self.driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                            like_index += 1

                            self.update.emit(f"좋아요 {like_index}개 성공!")
                            time.sleep(2)

                        # 좋아요를 모두 누른 경우
                        else:
                            print("좋아요 pass")
                            pass
                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.CONTROL + "\n")
                            tabs = self.driver.window_handles
                            self.driver.switch_to.window(tabs[2])
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            self.driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.update.emit(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            comment_index += 1
                            time.sleep(2)
                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])

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


            # 아직 좋아요와 댓글이 남아 있는 경우
            if like_index < input_like or comment_index < input_add_comment:
                self.update.emit("\n남은 좋아요 및 댓글 작업을 시작합니다.\n")

                current_url = self.driver.current_url

                # like_index와 comment_index가 입력해놓은 숫자가 될 때까지 반복
                while like_index != input_like or comment_index != input_add_comment:

                    # 서이추가 0인 경우
                    if current_url == "data:,":
                        pass
                    
                    # 서이추 횟수까지는 모두 채운 경우
                    else:
                        blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")

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
                        blog_list = self.driver.find_elements(By.CSS_SELECTOR, ".name")

                        # 새창으로 드라이버 전환
                        tabs = self.driver.window_handles
                        self.driver.switch_to.window(tabs[1])

                        # 좋아요
                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                            time.sleep(1.5)

                            try:
                                time.sleep(input_speed_like)
                                # 좋아요 누르기
                                self.driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                                like_index += 1
                            except:
                                self.update.emit("좋아요 버튼이 없어 넘어갑니다.")
                                i += 1
                                continue
                            
                            
                            self.update.emit(f"좋아요 {like_index}개 성공!")
                            time.sleep(2)

                        # 좋아요를 모두 누른 경우
                        else:
                            print("좋아요 pass")
                            pass
                        
                        #=======================댓글 작업==========================

                        print(f"댓글 : {comment_index}, {input_add_comment}")

                        #  댓글을 입력해야 하는 경우
                        if comment_index < input_add_comment:

                            # 블로그 정렬 바꾸기
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = self.driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93").send_keys(Keys.ENTER)
                            time.sleep(2)

                            # 댓글 창 입력
                            self.driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
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

            self.update.emit("\n모든 서이추 및 댓글, 좋아요 작업 완료!")
            self.driver.quit()
            return 
        except:
            traceback_message = str(traceback.format_exc())
            self.update.emit(traceback_message)
            self.update.emit("\n* 오류가 발생했습니다.")

    def login(self, input_id, input_pw):

            # 크롬창 생성
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

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
                return 1
            
            # 로그인 실패
            else:
                self.driver.close()
                self.update.emit("로그인 실패")
                return 0


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
                                self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
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
                            self.driver.find_element(By.CSS_SELECTOR, "#contentslist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
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

        # 즉시 실행 버튼 클릭 이벤트
        self.start_btn_now.clicked.connect(self.main2)
        
        # 종료 버튼 클릭 이벤트
        self.exit_btn.clicked.connect(self.close)

        # 리셋 버튼 클릭 이벤트
        self.reset_btn.clicked.connect(self.reset)

        # 중지 버튼 클릭 이벤트
        self.stop_btn.clicked.connect(self.stop)

        # 이전 세팅값 불러오기
        settings = QSettings("블로그3", "이웃새글")
        self.id.setText(settings.value("id", ""))
        self.pw.setText(settings.value("pw", ""))

        self.search_keyword.setText(settings.value("keyword", ""))
        self.add_n.setValue(settings.value("add", 0, type=int))
        self.add_like.setValue(settings.value("add_like", 0, type=int))
        self.add_comment.setValue(settings.value("add_comment", 0, type=int))

        self.board.setText(settings.value("board", "이웃신청멘트를 입력하세요."))
        self.comment.setText(settings.value("comment", "댓글을 입력하세요."))

        self.speed_n.setValue(settings.value("speed_n", 0, type=int))
        self.speed_like.setValue(settings.value("speed_like", 0, type=int))
        self.speed_comment.setValue(settings.value("speed_comment", 0, type=int))

        self.reserve_2.hide()
        self.reserve_3.hide()
        self.reserve_4.hide()
        self.reserve_5.hide()

        # 예약설정 콤보 박스 바뀔 때
        self.reserve_setting.currentIndexChanged.connect(self.reserve_setting_changed)

    def main2(self):

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

        input_like = self.add_like.value()
        input_speed_n = self.speed_n.value()
        input_add_comment = self.add_comment.value()
        input_speed_like = self.speed_like.value()
        input_speed_comment = self.speed_comment.value()

        input_process = self.process.currentIndex()
        input_add_like2 = self.add_like2.value()
        input_add_comment2 = self.add_comment2.value()
        input_comment2 = self.comment2.toPlainText()

        # 유효성 검사
        if input_process == 0:
            if input_comment2 == "댓글을 입력하세요.":
                self.textBrowser.setText("빈칸을 모두 채워주세요.")
                return 0

        else:
            if input_id == "" or input_pw == "" or input_keyword == ""  or input_board == "이웃신청멘트를 입력하세요." or input_comment == '댓글을 입력하세요.':
                self.textBrowser.setText("빈칸을 모두 채워주세요.")
                return 0
        
        # 세팅값 저장하기
        settings = QSettings("블로그3", "이웃새글")
        settings.setValue("id", input_id)
        settings.setValue("pw", input_pw)
        settings.setValue("keyword", input_keyword)
        settings.setValue("add", input_add)
        settings.setValue("like", input_like)
        settings.setValue("add_comment", input_add_comment)
        settings.setValue("speed_n", input_speed_n)
        settings.setValue("board", input_board)
        settings.setValue("comment", input_comment)
        settings.setValue("speed_like", input_speed_like)
        settings.setValue("speed_comment", input_speed_comment)


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

        input_comment2 = input_comment2.split("\n")
        random.shuffle(input_comment2)

        # 딜레이 시간 받기
        first_delay = self.first_delay.value()
        last_delay = self.last_delay.value()

        # 블로그 별명 받기
        blog_nickname = self.blog_nickname.text()

        reserveTimes = 0

        self.second_thread = secondThread(reserveTimes, input_process, input_id, input_pw, input_keyword, input_add, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_add_like2, input_add_comment2, input_comment2, input_speed_comment, first_delay, last_delay, blog_nickname)
        self.second_thread.update.connect(self.update_text_browser)

        self.second_thread.start_signal.connect(self.update_start_signal)

        # Thread 실행
        self.second_thread.start()

    def reserve_setting_changed(self, index):

        if index == 0:
            self.reserve.show()
            self.reserve_2.hide()
            self.reserve_3.hide()
            self.reserve_4.hide()
            self.reserve_5.hide()

        elif index == 1:
            self.reserve.show()
            self.reserve_2.show()
            self.reserve_3.hide()
            self.reserve_4.hide()
            self.reserve_5.hide()

        elif index == 2:
            self.reserve.show()
            self.reserve_2.show()
            self.reserve_3.show()
            self.reserve_4.hide()
            self.reserve_5.hide()

        elif index == 3:
            self.reserve.show()
            self.reserve_2.show()
            self.reserve_3.show()
            self.reserve_4.show()
            self.reserve_5.hide()
        else:
            self.reserve.show()
            self.reserve_2.show()
            self.reserve_3.show()
            self.reserve_4.show()
            self.reserve_5.show()
            




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

        input_like = self.add_like.value()
        input_speed_n = self.speed_n.value()
        input_add_comment = self.add_comment.value()
        input_speed_like = self.speed_like.value()
        input_speed_comment = self.speed_comment.value()

        input_process = self.process.currentIndex()
        input_add_like2 = self.add_like2.value()
        input_add_comment2 = self.add_comment2.value()
        input_comment2 = self.comment2.toPlainText()

        # 유효성 검사
        if input_process == 0:
            if input_comment2 == "댓글을 입력하세요.":
                self.textBrowser.setText("빈칸을 모두 채워주세요.")
                return 0

        else:
            if input_id == "" or input_pw == "" or input_keyword == ""  or input_board == "이웃신청멘트를 입력하세요." or input_comment == '댓글을 입력하세요.':
                self.textBrowser.setText("빈칸을 모두 채워주세요.")
                return 0
        
        # 세팅값 저장하기
        settings = QSettings("블로그3", "이웃새글")
        settings.setValue("id", input_id)
        settings.setValue("pw", input_pw)
        settings.setValue("keyword", input_keyword)
        settings.setValue("add", input_add)
        settings.setValue("like", input_like)
        settings.setValue("add_comment", input_add_comment)
        settings.setValue("speed_n", input_speed_n)
        settings.setValue("board", input_board)
        settings.setValue("comment", input_comment)
        settings.setValue("speed_like", input_speed_like)
        settings.setValue("speed_comment", input_speed_comment)


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

        input_comment2 = input_comment2.split("\n")
        random.shuffle(input_comment2)

        # 설정 시간 받기
        current_reservetime = self.reserve_setting.currentIndex()
        reserveTimes = []
        if current_reservetime == 0:
            reserveTimes.append(self.reserve.time().toString("HH:mm"))
        
        elif current_reservetime == 1:
            reserveTimes.append(self.reserve.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_2.time().toString("HH:mm"))

        elif current_reservetime == 2:
            reserveTimes.append(self.reserve.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_2.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_3.time().toString("HH:mm"))

        elif current_reservetime == 3:
            reserveTimes.append(self.reserve.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_2.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_3.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_4.time().toString("HH:mm"))

        elif current_reservetime == 4:
            reserveTimes.append(self.reserve.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_2.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_3.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_4.time().toString("HH:mm"))
            reserveTimes.append(self.reserve_5.time().toString("HH:mm"))

        # 딜레이 시간 받기
        first_delay = self.first_delay.value()
        last_delay = self.last_delay.value()

        # 블로그 별명 받기
        blog_nickname = self.blog_nickname.text()
        blog_nickname = blog_nickname.strip()

        self.second_thread = secondThread(reserveTimes, input_process, input_id, input_pw, input_keyword, input_add, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_add_like2, input_add_comment2, input_comment2, input_speed_comment, first_delay, last_delay, blog_nickname)
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
        self.add_like.clear()
        self.comment.setText("댓글을 입력하세요.")
        

    # 종료 버튼 함수
    def close(self):
        sys.exit()
        
    

QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = first()
main_dialog.show()

sys.exit(app.exec_())
