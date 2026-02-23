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
from datetime import timedelta
import traceback
import random
from PyQt5.QtCore import QSettings

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
login_dict = {"dindin" : "070722"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "디노_서이추_프로그램.ui"

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

        # 이전 세팅값 불러오기
        settings = QSettings("디노", "서이추프로그램")
        self.id.setText(settings.value("id", ""))
        self.pw.setText(settings.value("pw", ""))
        self.search_keyword.setText(settings.value("keyword", ""))


        self.add_n.setValue(settings.value("add", 0, type=int))
        self.speed_n.setValue(settings.value("speed_n", 0, type=int))
        self.add_like.setValue(settings.value("like", 0, type=int))
        self.add_comment.setValue(settings.value("add_comment", 0, type=int))
        self.speed_like.setValue(settings.value("speed_like", 0, type=int))

        self.managing.setChecked(settings.value("managing", False, type=bool))


        self.board.setText(settings.value("board", "이웃신청멘트를 입력하세요."))
        self.comment.setText(settings.value("comment", "댓글을 입력하세요."))





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

        t = self.clock.time().toString("HH:mm")

        print(t, type(t))

        # 유효성 검사
        if input_id == "" or input_pw == "" or input_keyword == ""  or input_board == "이웃신청멘트를 입력하세요." or input_comment == '댓글을 입력하세요.':
            self.textBrowser.setText("빈칸을 모두 채워주세요.")
            return 0
        
        # 세팅값 저장하기
        settings = QSettings("디노", "서이추프로그램")
        settings.setValue("id", input_id)
        settings.setValue("pw", input_pw)
        settings.setValue("keyword", input_keyword)
        settings.setValue("add", input_add)
        settings.setValue("like", input_like)
        settings.setValue("add_comment", input_add_comment)
        settings.setValue("speed_n", input_speed_n)
        settings.setValue("managing", self.managing.isChecked())
        settings.setValue("board", input_board)
        settings.setValue("comment", input_comment)
        settings.setValue("speed_like", input_speed_like)


        self.textBrowser.setText("")

        # 세팅값 저장 때문에 뒤늦게 처리
        input_keyword = self.search_keyword.text().split(',')

        # 이웃신청멘트 값 리스트로 전환 후 랜덤
        input_board = input_board.split("\n")
        random.shuffle(input_board)

        # 댓글 값 리스트 전환 후 랜덤
        input_comment = input_comment.split("\n")
        random.shuffle(input_comment)





                
        # 로그인 진행
        self.textBrowser.append("로그인 진행중...")
        QApplication.processEvents()
        
        # 로그인 메서드 실행
        driver = self.login(input_id, input_pw)


        if driver == 0:
            self.textBrowser.setText("로그인 실패")
            QApplication.processEvents()
            return 0
        
        # 이웃추가 메서드 실행
        else:
            self.textBrowser.append("로그인 성공...")
            QApplication.processEvents()
            self.textBrowser.append("자동화 진행중...")
            QApplication.processEvents()    
        
            driver = self.neighbor_add(driver, input_keyword, input_add, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_id)
        
        # 이웃관리 진행
        if self.managing.isChecked():
            driver = self.manage_neighbor(driver, input_id)

        self.textBrowser.append("\n* 모든 자동화 완료! *")
        QApplication.processEvents()

        try:
            driver.quit()

        except:
            self.textBrowser.append("driver 오류")
            QApplication.processEvents()

        self.textBrowser.append("\n다음 자동화까지 대기중...")
        QApplication.processEvents()

        # 다음 시간에 맞추어 실행
        
        while 1:
            
            # 현재 시간 연속 갱신
            now = datetime.now()
            now = now.strftime('%H:%M')

            if t == now:
        
                self.textBrowser.setText("")
                
                # 로그인 진행
                self.textBrowser.append("로그인 진행중...")
                QApplication.processEvents()
                
                # 로그인 메서드 실행
                driver = self.login(input_id, input_pw)


                if driver == 0:
                    self.textBrowser.setText("로그인 실패")
                    QApplication.processEvents()
                    return 0
                
                # 이웃추가 메서드 실행
                else:
                    self.textBrowser.append("로그인 성공...")
                    QApplication.processEvents()
                    self.textBrowser.append("자동화 진행중...")
                    QApplication.processEvents()    
                
                    driver = self.neighbor_add(driver, input_keyword, input_add, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_id)
                
                # 이웃관리 진행
                if self.managing.isChecked():
                    driver = self.manage_neighbor(driver, input_id)

                self.textBrowser.append("\n* 모든 자동화 완료! *")
                QApplication.processEvents()

                try:
                    driver.quit()

                except:
                    self.textBrowser.append("driver 오류")
                    QApplication.processEvents()

                self.textBrowser.append("\n다음 자동화까지 대기중...")
                QApplication.processEvents()

            else:
                continue


#===============================================================================================================
    
    def login(self, input_id, input_pw):

        # 크롬창 생성
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 웹페이지 해당 주소 이동
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")

        time.sleep(3)

        # 아이디 입력
        id = driver.find_element(By.CSS_SELECTOR, "#id")
        id.click()
        pyperclip.copy(input_id)
        pyautogui.hotkey("ctrl", "v")


        # 비밀번호 입력
        pw = driver.find_element(By.CSS_SELECTOR, "#pw")
        pw.click()
        pyperclip.copy(input_pw)
        pyautogui.hotkey("ctrl", "v")


        # 로그인 버튼
        login_btn = driver.find_element(By.CSS_SELECTOR, "#log\.login")
        login_btn.click()

        # 로그인 브라우저 등록
        try:
            driver.find_element(By.CSS_SELECTOR, "#new\.save").click()
        except:
            pass


        # 로그인 완료
        # 로그인 성공 시 드라이버 반환
        # 로그인 실패 시 드라이버 종료 후  0 반환

        check = driver.find_elements(By.CSS_SELECTOR, ".MyView-module__my_info___GNmHz")

        # 로그인 성공
        if len(check) > 0:
            return driver
        
        # 로그인 실패
        else:
            driver.close()
            return 0
        

    # 이웃수, 공감, 댓글 싸그리
    def neighbor_add(self, driver, input_keyword, n, input_board, input_speed_n, input_like, input_comment, input_add_comment, input_speed_like, input_id):
        
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
                driver.get(url)
                
                # 블로그 리스트의 사용할 인덱스
                i = 0

                # 평균만큼 실행할 인덱스
                avg = 0

                # 키워드 리스트의 평균만큼 진행
                while avg < cnt:

                    print(f"i : {i}, cnt : {cnt}")
                    
                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")

                    print(f"블로그 리스트 : {len(blog_list)}, 이웃 인덱스 : {neighbor_index}")

                    try:
                        # 블로그 아이디 클릭
                        # 현재 블로그 글 번호에 맞는 아이디 찾기
                        blog = blog_list[i]
                        blog.send_keys(Keys.END)
                    except:
                        self.textBrowser.append("더 이상 해당 키워드에 블로그가 없습니다.")
                        QApplication.processEvents()
                        break

                    # 새창으로 열기
                    blog.send_keys(Keys.CONTROL + "\n")
                    time.sleep(2)
                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")

                    # 새창으로 드라이버 전환
                    tabs = driver.window_handles
                    driver.switch_to.window(tabs[1])

                    current_blog_url = driver.current_url
                
                    try:
                        print("이웃추가 try")
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                        driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B")

                        driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B").send_keys(Keys.ENTER)
                        time.sleep(1)

                        # 이웃 수가 5000명 초과 경우
                        try:
                            over_neighbor = driver.find_element(By.CSS_SELECTOR, ".desc__LlxVe").text
                            print(over_neighbor)
                            print("5,000" in over_neighbor)
                            if "5,000" in over_neighbor:
                                self.manage_over_neighbor(driver, input_id)
                                time.sleep(1)

                                print("5000명 초과 작업 끝")

                                driver.close()
                                tabs = driver.window_handles
                                driver.switch_to.window(tabs[0])

                                self.textBrowser.append("서이추 작업을 재개합니다.")
                                QApplication.processEvents()
                                continue
                        except:
                            print("except")
                            pass
                        
                        
                        # 서로 이웃 추가 버튼 클릭
                        driver.find_element(By.CSS_SELECTOR,"#bothBuddyRadio").click()
                        time.sleep(1)



                    except:
                        self.textBrowser.append("\n서이추 또는 좋아요 버튼이 없어 다음으로 넘어갑니다.\n")
                        QApplication.processEvents()
                        i += 1

                        driver.close()
                        driver.switch_to.window(tabs[0])
                        continue

                    else:
                        
                        try:
                            # 멘트 남기기
                            text_area = driver.find_element(By.CSS_SELECTOR,"#buddyAddForm > fieldset > div > div.set_detail_t1 > div.set_detail_t1 > div > textarea")
                            text_area.click()
                            text_area.send_keys(Keys.CONTROL, "a")
                            text_area.send_keys(Keys.DELETE)
                            text_area.send_keys(f"{input_board[random.randint(0, len(input_board) - 1)]}")

                        except:
                            self.textBrowser.append("\n서로이웃신청이 불가하여 다음으로 넘어갑니다.\n")
                            QApplication.processEvents()
                            i += 1

                            driver.close()
                            driver.switch_to.window(tabs[0])
                            continue

                        # 그룹 선택
                        groups = driver.find_elements(By.CSS_SELECTOR, "#buddyGroupSelect > option")
                        group_idx = 0
                        group_err = 0

                        while group_idx < len(groups):
                            
                            try:
                                groups[group_idx].click()
                                time.sleep(1)

                            except:
                                print("그룹 선택에 오류가 발생했습니다.")
                                self.textBrowser.append("그룹 선택에 오류가 발생했습니다.")
                                self.textBrowser.append(f"groups = {len(groups)}, group_idx = {group_idx}, group_err = {group_err}")
                                self.textBrowser.append("재시도 합니다.")
                                QApplication.processEvents()
                                print(groups, group_idx, group_err)
                                continue

                            # 이웃초과가 한번 떴을 경우
                            if group_err > 0:
                                driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)

                                over_alert = driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

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
                                driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)
                                
                                
                                over_alert = driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

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
                            self.textBrowser.appeend("이웃그룹의 정원이 모두 찼습니다.")
                            self.textBrowser.appeend("프로그램을 종료합니다.")
                            QApplication.processEvents()
                            break

                        else:
                            neighbor_index += 1

            
                        # 이웃추가 완료 문구 띄우기
                        self.textBrowser.append(f"\n이웃추가 {neighbor_index}개 완료!")
                        QApplication.processEvents()

                        driver.get(current_blog_url)
                        time.sleep(1)
                        
                        # 블로그 정렬 바꾸기
                        driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        #===================좋아요 과정 ============================
                        
                        print(f"좋아요 : {like_index}, {input_like}")

                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            # 좋아요 누르기
                            time.sleep(input_speed_like)
                            driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                            like_index += 1

                            self.textBrowser.append(f"좋아요 {like_index}개 성공!")
                            QApplication.processEvents()
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
                            reply_btn = driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.CONTROL + "\n")
                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[2])
                            time.sleep(2)

                            # 댓글 창 입력
                            driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.textBrowser.append(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            QApplication.processEvents()
                            comment_index += 1
                            time.sleep(2)
                            driver.close()
                            driver.switch_to.window(tabs[1])

                        else:
                            print("댓글 pass")
                            pass


                    print("탭을 닫습니다.")
                    # 현재 탭 닫기
                    driver.close()
                    driver.switch_to.window(tabs[0])
                    i += 1
                    avg += 1



                self.textBrowser.append("다음 키워드로 넘어갑니다.\n")
                QApplication.processEvents()

    ###################### 1차 작업 끝 ###################################

            # 아직 목표 서이추 수를 도달하지 못한 경우
            if neighbor_index < n:
                print("목표 서이추 수 미도달")
                self.textBrowser.append("키워드가 없어 현재 키워드로 진행합니다.\n")
                QApplication.processEvents()

                while neighbor_index < n:

                    print(f"neighbor_index : {neighbor_index}, n : {n}")

                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")
                    print(f"블로그 리스트 길이 : {len(blog_list)}, i : {i}")
                    
                    try:
                        # 블로그 아이디 클릭
                        # 현재 블로그 글 번호에 맞는 아이디 찾기
                        blog = blog_list[i]
                        blog.send_keys(Keys.PAGE_DOWN)
                    except:
                        self.textBrowser.append("인덱스 아웃 오브 레인지")
                        QApplication.processEvents()
                        break

                    # 새창으로 열기
                    blog.send_keys(Keys.CONTROL + "\n")
                    time.sleep(2)
                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")

                    # 새창으로 드라이버 전환
                    tabs = driver.window_handles
                    driver.switch_to.window(tabs[1])

                    current_blog_url = driver.current_url
                
                    try:
                        # 이웃 추가 버튼 클릭
                        time.sleep(2.5)
                        driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off")
                        driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B")

                        driver.find_element(By.CSS_SELECTOR,".link__RsHMX.add_buddy_btn__oGR_B").send_keys(Keys.ENTER)
                        time.sleep(1)
                        
                        # 서로 이웃 추가 버튼 클릭
                        driver.find_element(By.CSS_SELECTOR,"#bothBuddyRadio").click()

                    except:
                        self.textBrowser.append("\n서이추 또는 좋아요 버튼이 없어 다음으로 넘어갑니다.\n")
                        QApplication.processEvents()
                        i += 1

                        driver.close()
                        driver.switch_to.window(tabs[0])
                        continue

                    else:

                        try:
                            # 멘트 남기기
                            text_area = driver.find_element(By.CSS_SELECTOR,"#buddyAddForm > fieldset > div > div.set_detail_t1 > div.set_detail_t1 > div > textarea")
                            text_area.click()
                            text_area.send_keys(Keys.CONTROL, "a")
                            text_area.send_keys(Keys.DELETE)
                            text_area.send_keys(f"{input_board[random.randint(0, len(input_board) - 1)]}")

                        except:
                            self.textBrowser.append("\n서로이웃신청이 불가하여 다음으로 넘어갑니다.\n")
                            QApplication.processEvents()
                            i += 1

                            driver.close()
                            driver.switch_to.window(tabs[0])
                            continue

                        # 그룹 선택
                        groups = driver.find_elements(By.CSS_SELECTOR, "#buddyGroupSelect > option")
                        group_idx = 0
                        group_err = 0

                        while group_idx < len(groups):
                            
                            try:
                                groups[group_idx].click()
                                time.sleep(1)
                            except:
                                print("그룹 선택에 오류가 발생했습니다.")
                                self.textBrowser.append("그룹 선택에 오류가 발생했습니다.")
                                self.textBrowser.append(f"groups = {len(groups)}, group_idx = {group_idx}, group_err = {group_err}")
                                self.textBrowser.append("재시도 합니다.")
                                QApplication.processEvents()
                                print(groups, group_idx, group_err)
                                continue

                            # 이웃초과가 한번 떴을 경우
                            if group_err > 0:
                                driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)

                                over_alert = driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

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
                                driver.find_element(By.CSS_SELECTOR,".btn_ok").click()
                                time.sleep(0.3)
                                
                                
                                over_alert = driver.find_elements(By.CSS_SELECTOR, "#_alertLayerClose")

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
                            self.textBrowser.appeend("이웃그룹의 정원이 모두 찼습니다.")
                            self.textBrowser.appeend("프로그램을 종료합니다.")
                            QApplication.processEvents()
                            break

                        else:
                            neighbor_index += 1

            
                        # 이웃추가 완료 문구 띄우기
                        self.textBrowser.append(f"\n이웃추가 {neighbor_index}개 완료!")
                        QApplication.processEvents()

                        driver.get(current_blog_url)
                        time.sleep(1)

                        # 블로그 정렬 바꾸기
                        driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                        time.sleep(1.5)

                        #===================좋아요 과정 ============================
                        
                        print(f"좋아요 : {like_index}, {input_like}")

                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            time.sleep(input_speed_like)
                            # 좋아요 누르기
                            driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                            like_index += 1

                            self.textBrowser.append(f"좋아요 {like_index}개 성공!")
                            QApplication.processEvents()
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
                            driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93")

                            # 댓글 버튼 클릭 + 새 창으로 열기
                            reply_btn.send_keys(Keys.CONTROL + "\n")
                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[2])
                            time.sleep(2)

                            # 댓글 창 입력
                            driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.textBrowser.append(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            QApplication.processEvents()
                            comment_index += 1
                            time.sleep(2)
                            driver.close()
                            driver.switch_to.window(tabs[1])

                        else:
                            print("댓글 pass")
                            pass


                        # 완료된 작업 실시간 반영
                        self.textBrowser.append("\n")
                        QApplication.processEvents()

                    print("탭을 닫습니다.")
                    # 현재 탭 닫기
                    driver.close()
                    driver.switch_to.window(tabs[0])
                    i += 1




            # 아직 좋아요와 댓글이 남아 있는 경우
            if like_index < input_like or comment_index < input_add_comment:
                self.textBrowser.append("\n남은 좋아요 및 댓글 작업을 시작합니다.\n")
                QApplication.processEvents()

                current_url = driver.current_url

                # like_index와 comment_index가 입력해놓은 숫자가 될 때까지 반복
                while like_index != input_like or comment_index != input_add_comment:

                    # 서이추가 없는 경우
                    if current_url == "data:,":
                        pass
                    
                    # 서이추 횟수까지는 모두 채운 경우
                    else:
                        blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")

                        try:
                            # 블로그 아이디 클릭
                            # 현재 블로그 글 번호에 맞는 아이디 찾기
                            blog = blog_list[i]
                            blog.send_keys(Keys.PAGE_DOWN)
                        except:
                            self.textBrowser.append("인덱스 아웃 오브 레인지")
                            QApplication.processEvents()
                            break

                        # 새창으로 열기
                        blog.send_keys(Keys.CONTROL + "\n")
                        time.sleep(2)
                        blog_list = driver.find_elements(By.CSS_SELECTOR, ".name")

                        # 새창으로 드라이버 전환
                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[1])

                        # 좋아요
                        # 좋아요를 눌러야하는 경우
                        if like_index < input_like:

                            # 블로그 정렬 바꾸기
                            driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                            time.sleep(1.5)

                            try:
                                time.sleep(input_speed_like)
                                # 좋아요 누르기
                                driver.find_element(By.CSS_SELECTOR,".u_likeit_list_btn._button.off").send_keys(Keys.ENTER)
                                like_index += 1
                            except:
                                self.textBrowser.append("좋아요 버튼이 없어 넘어갑니다.")
                                QApplication.processEvents()
                                i += 1
                                continue
                            

                            self.textBrowser.append(f"좋아요 {like_index}개 성공!")
                            QApplication.processEvents()
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
                            driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)

                            # 이웃추가한 블로그에 글 리스트 받아서 댓글 입력하기
                            # 댓글 버튼들 리스트로 받기
                            reply_btn = driver.find_element(By.CSS_SELECTOR, ".comment_btn__lcx93").send_keys(Keys.ENTER)
                            time.sleep(2)

                            # 댓글 창 입력
                            driver.find_element(By.CSS_SELECTOR, "#naverComment__write_textarea").send_keys(input_comment[random.randint(0, len(input_comment) - 1)])
                            driver.find_element(By.CSS_SELECTOR, ".u_cbox_btn_upload").click()
                            self.textBrowser.append(f"댓글 {comment_index + 1}개 입력 완료!\n")
                            QApplication.processEvents()
                            comment_index += 1
                            time.sleep(2)
                            driver.close()
                            driver.switch_to.window(tabs[0])

                        else:
                            print("댓글 pass")
                            driver.close()
                            driver.switch_to.window(tabs[0])
                            pass

                        # 완료된 작업 실시간 반영
                        self.textBrowser.append("\n")
                        QApplication.processEvents()

                        i += 1

            self.textBrowser.append("\n모든 서이추 및 댓글, 좋아요 작업 완료!")
            QApplication.processEvents()
            return driver
        except:
            traceback_message = str(traceback.format_exc())
            self.textBrowser.append(traceback_message)
            self.textBrowser.append("\n* 오류가 발생했습니다.")
            QApplication.processEvents()


        
    def manage_over_neighbor(self, driver, input_id):
        
        self.textBrowser.append("\n이웃 수가 5000명이 넘어 이웃관리로 넘어갑니다.\n")
        QApplication.processEvents()
        try:
            driver.get(f"https://admin.blog.naver.com/{input_id}")
            time.sleep(2)

            driver.find_element(By.CSS_SELECTOR, "#buddyinvite_config_anchor").click()
            print("서로이웃 신청 메뉴 클릭")

            time.sleep(2)

            driver.switch_to.frame("papermain")

            # 보낸신청 메뉴 클릭
            driver.find_element(By.CSS_SELECTOR, "#inviteMe > ul > li._nclk\(bas_neitadd\.send\) > a").click()

            try:
                # 신청일 리스트
                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
            except:
                print("보낸 신청이 없습니다.")
                self.textBrowser.append("보낸 신청이 없습니다.")
                QApplication.processEvents()
                return driver
                

            # date의 text를 담아두는 리스트
            date_list = []

            for i in range(len(dates)):
                date_list.append(dates[i].text.replace(".", "-")[:-1])

            # 신청한 사람 리스트
            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

            # 신청취소 버튼 리스트
            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

            current_date_time = datetime.now()

            # 2주(14일) 전의 날짜 계산
            two_weeks_ago = current_date_time - timedelta(days=14)

            # 날짜 형식화 (예: YYYY-MM-DD)
            two_weeks_ago = two_weeks_ago.strftime("%Y-%m-%d")[2:]

            # 6개월 전 날짜 계산
            six_months_ago = current_date_time - timedelta(days=180)
            six_months_ago = six_months_ago.strftime("%Y-%m-%d")[2:]

            a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
            a_index = 0

            ########################### 다음 페이지들이 있는 경우 ###########################
            if len(a) > 0:

                while 1:

                    self.textBrowser.append("\n다음 페이지로\n")
                    QApplication.processEvents()

                    try:
                        # 신청일 리스트
                        dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                    except:
                        print("보낸 신청이 없습니다.")
                        self.textBrowser.append("보낸 신청이 없습니다.")
                        QApplication.processEvents()
                        return driver
                    

                    # date의 text를 담아두는 리스트
                    date_list = []

                    for index in range(len(dates)):
                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                    # 신청한 사람 리스트
                    users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                    # 신청취소 버튼 리스트
                    cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                    i = 0

                    while i != len(dates) or i < len(dates):

                        print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                        self.textBrowser.append(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}")
                        QApplication.processEvents()
                        
                        # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                        if date_list[i] <= two_weeks_ago:
                            print("2주 이상 지남 -> 삭제 대상")
                            self.textBrowser.append("2주 이상 지남 -> 삭제 대상\n")
                            QApplication.processEvents()

                            t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                print("1페이지가 아님")
                                time.sleep(1.5)
                                a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                a[a_index-1].click()
                                time.sleep(1.5)


                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue
                            


                        # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                        else:
                            # 블로그 6개월 활동 확인
                            users[i].click()

                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[2])
                            time.sleep(1)
                            url = driver.current_url

                            # url 모바일로 변경
                            url = url[:8] + "m." + url[8:]

                            driver.get(url)
                            time.sleep(4)

                            try:
                                # 블로그 정렬 바꾸기
                                driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                                time.sleep(1)
                            
                            except:
                                print("비정상 블로그 -> 삭제")
                                self.textBrowser.append("비정상 블로그 -> 삭제\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[1])

                                driver.switch_to.frame("papermain")

                                t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                                
                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue


                            # 블로그 최신글 날짜 추출
                            try:
                                blog_time = driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                                QApplication.processEvents()
                            except:
                                self.textBrowser.append("게시물이 없는 블로그 -> 유지")
                                QApplication.processEvents()
                                driver.close()
                                driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                            # 먼저 hh시간전, mm분인 블로그 색출
                            if "시간" in blog_time or "분" in blog_time:
                                print("hh시간전, mm분인 블로그 -> 유지")
                                self.textBrowser.append("hh시간전, mm분인 블로그 -> 유지\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            
                            # 6개월전 블로그 색출
                            else:

                                blog_time = blog_time.replace(". ", "-")[2 : -1]

                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                                QApplication.processEvents()

                                # 최신글이 6개월 이상 된 경우
                                if blog_time < six_months_ago:
                                    print("6개월 이상됨 -> 삭제 대상")
                                    self.textBrowser.append("6개월 이상됨 -> 삭제 대상\n")
                                    QApplication.processEvents()

                                    driver.close()
                                    driver.switch_to.window(tabs[1])
                                    time.sleep(2)

                                    driver.switch_to.frame("papermain")

                                    # 현재 페이지 저장
                                    t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                    time.sleep(2)
                                    # 신청 취소
                                    cancels[i].click()
                                    time.sleep(2)

                                    # 경고창 확인
                                    result = driver.switch_to.alert
                                    result.accept()
                                    result.dismiss()

                                    driver.switch_to.window(tabs[1])
                                    time.sleep(0.5)
                                    driver.switch_to.frame("papermain")

                                    # 현재 페이지로 회귀
                                    if t > 1:
                                        print("1페이지가 아님")
                                        time.sleep(1.5)
                                        a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                        a[a_index-1].click()
                                        time.sleep(1.5)

                                    # 요소들 새로고침
                                    # 신청일 리스트
                                    dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                    # date의 text를 담아두는 리스트
                                    date_list = []

                                    for index in range(len(dates)):
                                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                                    # 신청한 사람 리스트
                                    users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                    # 신청취소 버튼 리스트
                                    cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                    continue

                                # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                                else:
                                    print("활동중인 블로그 -> 유지")
                                    self.textBrowser.append("활동중인 블로그 -> 유지\n")
                                    QApplication.processEvents()

                                    driver.close()
                                    driver.switch_to.window(tabs[1])
                                    time.sleep(2)
                                    driver.switch_to.frame("papermain")
                                    i += 1
                                    continue

                    # 다음 페이지들의 리스트
                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")

                    try:
                        a[a_index].click()
                        time.sleep(2)
                        a_index += 1
                        continue

                    except:
                        print("페이지 끝")
                        self.textBrowser.append("\n페이지 끝\n")
                        QApplication.processEvents()
                        self.textBrowser.append("이웃관리 완료!")
                        QApplication.processEvents()
                        return
                        


                    


            ########################### 현재 페이지가 끝인 경우 ########################
            else:
                print("현재 페이지가 마지막입니다.")
                self.textBrowser.append("현재 페이지가 마지막입니다.")
                QApplication.processEvents()

                try:
                    # 신청일 리스트
                    dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                except:
                    print("보낸 신청이 없습니다.")
                    self.textBrowser.append("보낸신청이 없습니다.")
                    QApplication.processEvents()
                    self.textBrowser.append("\n모든 이웃관리 완료!\n")
                    return
                    
                

                # date의 text를 담아두는 리스트
                date_list = []

                for index in range(len(dates)):
                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                # 신청한 사람 리스트
                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                # 신청취소 버튼 리스트
                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                i = 0

                while i != len(dates) or i < len(dates):

                    print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                    self.textBrowser.append(f"\nuser : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}\n")
                    QApplication.processEvents()

                    # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                    if date_list[i] <= two_weeks_ago:
                        print("2주 이상 지남 -> 삭제 대상")
                        self.textBrowser.append("2주 이상 지남 -> 삭제 대상\n")
                        QApplication.processEvents()

                        t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                        time.sleep(2)
                        # 신청 취소
                        cancels[i].click()
                        time.sleep(2)

                        # 경고창 확인
                        result = driver.switch_to.alert
                        result.accept()
                        result.dismiss()

                        # 현재 페이지로 회귀
                        if t > 1:
                            print("1페이지가 아님")
                            time.sleep(1.5)
                            a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                            a[a_index-1].click()
                            time.sleep(1.5)
                            

                        # 요소들 새로고침
                        # 신청일 리스트
                        dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                        # date의 text를 담아두는 리스트
                        date_list = []

                        for index in range(len(dates)):
                            date_list.append(dates[index].text.replace(".", "-")[:-1])

                        # 신청한 사람 리스트
                        users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                        # 신청취소 버튼 리스트
                        cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                        continue
                        


                    # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                    else:
                        # 블로그 6개월 활동 확인
                        users[i].click()

                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[2])
                        time.sleep(1)
                        url = driver.current_url

                        # url 모바일로 변경
                        url = url[:8] + "m." + url[8:]

                        driver.get(url)
                        time.sleep(4)

                        try:
                            # 블로그 정렬 바꾸기
                            driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                            time.sleep(1)
                        
                        except:
                            print("비정상 블로그 -> 삭제")
                            self.textBrowser.append("비정상 블로그 -> 삭제\n")
                            QApplication.processEvents()

                            driver.close()
                            driver.switch_to.window(tabs[1])

                            driver.switch_to.frame("papermain")

                            t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                            
                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                time.sleep(1.5)
                                a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                print("1페이지가 아님")
                                a[a_index-1].click()
                                time.sleep(1.5)

                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue


                        # 블로그 최신글 날짜 추출
                        try:
                            blog_time = driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                            print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                            self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                            QApplication.processEvents()
                        except:
                            self.textBrowser.append("게시물이 없는 블로그 -> 유지")
                            QApplication.processEvents()
                            driver.close()
                            driver.switch_to.window(tabs[1])
                            time.sleep(2)
                            driver.switch_to.frame("papermain")
                            i += 1
                            continue

                        # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                        # 먼저 hh시간전, mm분인 블로그 색출
                        if "시간" in blog_time or "분" in blog_time:
                            print("hh시간전, mm분인 블로그 -> 유지")
                            self.textBrowser.append("hh시간전, mm분인 블로그 -> 유지\n")
                            QApplication.processEvents()

                            driver.close()
                            driver.switch_to.window(tabs[1])
                            time.sleep(2)
                            driver.switch_to.frame("papermain")
                            i += 1
                            continue


                        
                        # 6개월전 블로그 색출
                        else:

                            blog_time = blog_time.replace(". ", "-")[2 : -1]

                            # 최신글이 6개월 이상 된 경우
                            if blog_time < six_months_ago:
                                print("6개월 이상됨 -> 삭제 대상")
                                self.textBrowser.append("6개월 이상됨 -> 삭제 대상\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[1])
                                time.sleep(2)

                                t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                driver.switch_to.window(tabs[1])
                                time.sleep(0.5)
                                driver.switch_to.frame("papermain")

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue

                            # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                            else:
                                print("활동중인 블로그 -> 유지")
                                self.textBrowser.append("활동중인 블로그 -> 유지\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue
                
                self.textBrowser.append("\n이웃관리 완료!\n")
                QApplication.processEvents()
                return

        except:
            traceback_message = str(traceback.format_exc())
            self.textBrowser.append(traceback_message)
            self.textBrowser.append("\n* 오류가 발생했습니다.")
            QApplication.processEvents()
            while 1:
                QApplication.processEvents()




                    




#=============================================================================================================
    def manage_neighbor(self, driver, input_id):

        self.textBrowser.append("\n이웃관리 진행중...\n")
        QApplication.processEvents()

        try:

            # 해당 메서드 프로세스
            # 1. 서로이웃신청 전체수락 -> 2. 받지 않은 블로거들 삭제
            driver.get(f"https://admin.blog.naver.com/{input_id}")
            time.sleep(2)


            ########################## 1. 서로이웃신청 전체수락 과정 #############################
                    
            driver.find_element(By.CSS_SELECTOR, "#buddylist_config_anchor").click()

            print("내가 추가한 이웃 클릭")

            # 이웃그룹 선택하기 위해 iframe 접속
            driver.switch_to.frame("papermain")
            driver.find_element(By.CSS_SELECTOR, "#wrap > ul > li._nclk\(bas_neimgr\.gnei\) > a").click()
            print("이웃그룹 클릭")

            time.sleep(2)

            # 이웃수 리스트
            neighbor_num_list = driver.find_elements(By.CSS_SELECTOR, ".num")[ : : 2]

            neighbor_index = 0

            # 내 이웃그룹 500미만 탐색
            for neighbor_num in neighbor_num_list:
                neighbor_num = int(neighbor_num.text)

                if neighbor_num < 500:
                    break
                else:
                    neighbor_index += 1

            print(f"이웃 인덱스 : {neighbor_index}")

            # iframe 탈출
            driver.switch_to.default_content()

            driver.find_element(By.CSS_SELECTOR, "#buddyinvite_config_anchor").click()
            print("서로이웃 신청 메뉴 클릭")

            time.sleep(2)

            driver.switch_to.frame("papermain")
            a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")

            hrefs = [element.get_attribute("href") for element in a]
            print(hrefs)

            # 받은 신청이 없는 경우
            try:
                driver.find_element(By.CSS_SELECTOR, ".none")
                self.textBrowser.append("받은 신청이 없습니다.")
                QApplication.processEvents()

            except:

                for i in range(len(hrefs) + 1):

                    while 1:
                        
                        # 전체선택 -> 수락
                        driver.find_element(By.CSS_SELECTOR, "#inviteMe > div:nth-child(7) > div > span.all_select > input").click()
                        print("전체선택 클릭")
                        
                        driver.find_element(By.CSS_SELECTOR, "#inviteMe > div:nth-child(7) > div > span:nth-child(2) > button").click()
                        print("수락 클릭")

                        time.sleep(2)

                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[1])
                        time.sleep(1)

                        # 그룹 선택
                        groups = driver.find_elements(By.CSS_SELECTOR, "#groupIdSelector > option")
                        groups[neighbor_index].click()

                        # 확인
                        driver.find_element(By.CSS_SELECTOR, "#footer > input[type=image]").click()
                        time.sleep(3)

                        is_err = driver.find_elements(By.CSS_SELECTOR, ".ngb_err")
                        print(len(is_err))

                        # 에러인 경우
                        if len(is_err) != 0:
                            print("error")
                            driver.find_element(By.CSS_SELECTOR ,"#footer > input[type=image]").click()
                            print("확인")
                            neighbor_index += 1
                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[0])
                            driver.switch_to.frame("papermain")
                            time.sleep(1)
                            continue

                        else:
                            print("통과")
                            driver.find_element(By.CSS_SELECTOR ,"#footer > input[type=image]").click()
                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[0])
                            driver.switch_to.frame("papermain")
                            break

                    self.textBrowser.append("\n이웃신청 전체수락 완료!\n")
                    QApplication.processEvents()

            ########################### 2. 받지 않은 블로거들 삭제 ###################################

            self.textBrowser.append("이웃신청 받지 않은 블로거 삭제 작업중...\n")
            QApplication.processEvents()
            
            driver.get(f"https://admin.blog.naver.com/{input_id}")

            driver.find_element(By.CSS_SELECTOR, "#buddyinvite_config_anchor").click()
            print("서로이웃 신청 메뉴 클릭")

            time.sleep(2)

            driver.switch_to.frame("papermain")

            # 보낸신청 메뉴 클릭
            driver.find_element(By.CSS_SELECTOR, "#inviteMe > ul > li._nclk\(bas_neitadd\.send\) > a").click()

            try:
                # 신청일 리스트
                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
            except:
                print("보낸 신청이 없습니다.")
                self.textBrowser.append("보낸 신청이 없습니다.")
                QApplication.processEvents()
                return driver
                

            # date의 text를 담아두는 리스트
            date_list = []

            for i in range(len(dates)):
                date_list.append(dates[i].text.replace(".", "-")[:-1])

            # 신청한 사람 리스트
            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

            # 신청취소 버튼 리스트
            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

            current_date_time = datetime.now()

            # 2주(14일) 전의 날짜 계산
            two_weeks_ago = current_date_time - timedelta(days=14)

            # 날짜 형식화 (예: YYYY-MM-DD)
            two_weeks_ago = two_weeks_ago.strftime("%Y-%m-%d")[2:]

            # 6개월 전 날짜 계산
            six_months_ago = current_date_time - timedelta(days=180)
            six_months_ago = six_months_ago.strftime("%Y-%m-%d")[2:]

            a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
            a_index = 0

            ########################### 다음 페이지들이 있는 경우 ###########################
            if len(a) > 0:

                while 1:

                    self.textBrowser.append("\n다음 페이지로\n")
                    QApplication.processEvents()

                    try:
                        # 신청일 리스트
                        dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                    except:
                        print("보낸 신청이 없습니다.")
                        self.textBrowser.append("보낸 신청이 없습니다.")
                        QApplication.processEvents()
                        return driver
                    

                    # date의 text를 담아두는 리스트
                    date_list = []

                    for index in range(len(dates)):
                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                    # 신청한 사람 리스트
                    users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                    # 신청취소 버튼 리스트
                    cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                    i = 0

                    while i != len(dates) or i < len(dates):

                        print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                        self.textBrowser.append(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}")
                        QApplication.processEvents()
                        
                        # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                        if date_list[i] <= two_weeks_ago:
                            print("2주 이상 지남 -> 삭제 대상")
                            self.textBrowser.append("2주 이상 지남 -> 삭제 대상\n")
                            QApplication.processEvents()

                            t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                print("1페이지가 아님")
                                time.sleep(1.5)
                                a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                a[a_index-1].click()
                                time.sleep(1.5)


                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue
                            


                        # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                        else:
                            # 블로그 6개월 활동 확인
                            users[i].click()

                            tabs = driver.window_handles
                            driver.switch_to.window(tabs[1])
                            time.sleep(1)
                            url = driver.current_url

                            # url 모바일로 변경
                            url = url[:8] + "m." + url[8:]

                            driver.get(url)
                            time.sleep(4)

                            try:
                                # 블로그 정렬 바꾸기
                                driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                                time.sleep(1)
                            
                            except:
                                print("비정상 블로그 -> 삭제")
                                self.textBrowser.append("비정상 블로그 -> 삭제\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[0])

                                driver.switch_to.frame("papermain")

                                t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                                
                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue


                            # 블로그 최신글 날짜 추출
                            try:
                                blog_time = driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                                QApplication.processEvents()
                            except:
                                self.textBrowser.append("게시물이 없는 블로그 -> 유지")
                                QApplication.processEvents()
                                driver.close()
                                driver.switch_to.window(tabs[1])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                            # 먼저 hh시간전, mm분인 블로그 색출
                            if "시간" in blog_time or "분" in blog_time:
                                print("hh시간전, mm분인 블로그 -> 유지")
                                self.textBrowser.append("hh시간전, mm분인 블로그 -> 유지\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[0])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue

                            
                            # 6개월전 블로그 색출
                            else:

                                blog_time = blog_time.replace(". ", "-")[2 : -1]

                                print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                                self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                                QApplication.processEvents()

                                # 최신글이 6개월 이상 된 경우
                                if blog_time < six_months_ago:
                                    print("6개월 이상됨 -> 삭제 대상")
                                    self.textBrowser.append("6개월 이상됨 -> 삭제 대상\n")
                                    QApplication.processEvents()

                                    driver.close()
                                    driver.switch_to.window(tabs[0])
                                    time.sleep(2)

                                    driver.switch_to.frame("papermain")

                                    # 현재 페이지 저장
                                    t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                    time.sleep(2)
                                    # 신청 취소
                                    cancels[i].click()
                                    time.sleep(2)

                                    # 경고창 확인
                                    result = driver.switch_to.alert
                                    result.accept()
                                    result.dismiss()

                                    driver.switch_to.window(tabs[0])
                                    time.sleep(0.5)
                                    driver.switch_to.frame("papermain")

                                    # 현재 페이지로 회귀
                                    if t > 1:
                                        print("1페이지가 아님")
                                        time.sleep(1.5)
                                        a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                        a[a_index-1].click()
                                        time.sleep(1.5)

                                    # 요소들 새로고침
                                    # 신청일 리스트
                                    dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                    # date의 text를 담아두는 리스트
                                    date_list = []

                                    for index in range(len(dates)):
                                        date_list.append(dates[index].text.replace(".", "-")[:-1])

                                    # 신청한 사람 리스트
                                    users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                    # 신청취소 버튼 리스트
                                    cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                    continue

                                # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                                else:
                                    print("활동중인 블로그 -> 유지")
                                    self.textBrowser.append("활동중인 블로그 -> 유지\n")
                                    QApplication.processEvents()

                                    driver.close()
                                    driver.switch_to.window(tabs[0])
                                    time.sleep(2)
                                    driver.switch_to.frame("papermain")
                                    i += 1
                                    continue

                    # 다음 페이지들의 리스트
                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")

                    try:
                        a[a_index].click()
                        time.sleep(2)
                        a_index += 1
                        continue

                    except:
                        print("페이지 끝")
                        self.textBrowser.append("\n페이지 끝\n")
                        QApplication.processEvents()
                        self.textBrowser.append("모든 이웃관리 완료!")
                        QApplication.processEvents()
                        return driver


                    


            ########################### 현재 페이지가 끝인 경우 ########################
            else:
                print("현재 페이지가 마지막입니다.")
                self.textBrowser.append("현재 페이지가 마지막입니다.")
                QApplication.processEvents()

                try:
                    # 신청일 리스트
                    dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                except:
                    print("보낸 신청이 없습니다.")
                    self.textBrowser.append("보낸신청이 없습니다.")
                    QApplication.processEvents()
                    self.textBrowser.append("\n모든 이웃관리 완료!\n")
                    return
                    
                

                # date의 text를 담아두는 리스트
                date_list = []

                for index in range(len(dates)):
                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                # 신청한 사람 리스트
                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                # 신청취소 버튼 리스트
                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                i = 0

                while i != len(dates) or i < len(dates):

                    print(f"user : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}", date_list[i] <= two_weeks_ago)
                    self.textBrowser.append(f"\nuser : {users[i].text}, date : {date_list[i]}, 2주 전 날짜 : {two_weeks_ago}\n")
                    QApplication.processEvents()

                    # 2주 이상 지난 경우 (비교 대상 = <신청일> vs <현재 날짜에서 - 2주전>)
                    if date_list[i] <= two_weeks_ago:
                        print("2주 이상 지남 -> 삭제 대상")
                        self.textBrowser.append("2주 이상 지남 -> 삭제 대상\n")
                        QApplication.processEvents()

                        t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                        time.sleep(2)
                        # 신청 취소
                        cancels[i].click()
                        time.sleep(2)

                        # 경고창 확인
                        result = driver.switch_to.alert
                        result.accept()
                        result.dismiss()

                        # 현재 페이지로 회귀
                        if t > 1:
                            print("1페이지가 아님")
                            time.sleep(1.5)
                            a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                            a[a_index-1].click()
                            time.sleep(1.5)
                            

                        # 요소들 새로고침
                        # 신청일 리스트
                        dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                        # date의 text를 담아두는 리스트
                        date_list = []

                        for index in range(len(dates)):
                            date_list.append(dates[index].text.replace(".", "-")[:-1])

                        # 신청한 사람 리스트
                        users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                        # 신청취소 버튼 리스트
                        cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                        continue
                        


                    # 2주 이상 되지 않은 경우 -> 블로그 들어가서 활동중인 블로그인지 체크
                    else:
                        # 블로그 6개월 활동 확인
                        users[i].click()

                        tabs = driver.window_handles
                        driver.switch_to.window(tabs[1])
                        time.sleep(1)
                        url = driver.current_url

                        # url 모바일로 변경
                        url = url[:8] + "m." + url[8:]

                        driver.get(url)
                        time.sleep(4)

                        try:
                            # 블로그 정렬 바꾸기
                            driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button:nth-child(3)").send_keys(Keys.ENTER)
                            time.sleep(1)
                        
                        except:
                            print("비정상 블로그 -> 삭제")
                            self.textBrowser.append("비정상 블로그 -> 삭제\n")
                            QApplication.processEvents()

                            driver.close()
                            driver.switch_to.window(tabs[0])

                            driver.switch_to.frame("papermain")

                            t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)
                            
                            time.sleep(2)
                            # 신청 취소
                            cancels[i].click()
                            time.sleep(2)

                            # 경고창 확인
                            result = driver.switch_to.alert
                            result.accept()
                            result.dismiss()

                            # 현재 페이지로 회귀
                            if t > 1:
                                time.sleep(1.5)
                                a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                print("1페이지가 아님")
                                a[a_index-1].click()
                                time.sleep(1.5)

                            # 요소들 새로고침
                            # 신청일 리스트
                            dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                            # date의 text를 담아두는 리스트
                            date_list = []

                            for index in range(len(dates)):
                                date_list.append(dates[index].text.replace(".", "-")[:-1])

                            # 신청한 사람 리스트
                            users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                            # 신청취소 버튼 리스트
                            cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                            continue


                        # 블로그 최신글 날짜 추출
                        try:
                            blog_time = driver.find_element(By.CSS_SELECTOR, ".time__MHDWV").text
                            print(f"blog_time : {blog_time}, six_months_age : {six_months_ago}", blog_time < six_months_ago)
                            self.textBrowser.append(f"blog_time : {blog_time}, six_months_age : {six_months_ago}\n")
                            QApplication.processEvents()
                        except:
                            self.textBrowser.append("게시물이 없는 블로그 -> 유지")
                            QApplication.processEvents()
                            driver.close()
                            driver.switch_to.window(tabs[1])
                            time.sleep(2)
                            driver.switch_to.frame("papermain")
                            i += 1
                            continue

                        # 6개월전 색출 (비교 대상 = 현재 날짜에서 6개월 전 vs 블로그 최신글 날짜)
                        # 먼저 hh시간전, mm분인 블로그 색출
                        if "시간" in blog_time or "분" in blog_time:
                            print("hh시간전, mm분인 블로그 -> 유지")
                            self.textBrowser.append("hh시간전, mm분인 블로그 -> 유지\n")
                            QApplication.processEvents()

                            driver.close()
                            driver.switch_to.window(tabs[0])
                            time.sleep(2)
                            driver.switch_to.frame("papermain")
                            i += 1
                            continue


                        
                        # 6개월전 블로그 색출
                        else:

                            blog_time = blog_time.replace(". ", "-")[2 : -1]

                            # 최신글이 6개월 이상 된 경우
                            if blog_time < six_months_ago:
                                print("6개월 이상됨 -> 삭제 대상")
                                self.textBrowser.append("6개월 이상됨 -> 삭제 대상\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[0])
                                time.sleep(2)

                                t = int(driver.find_element(By.CSS_SELECTOR, ".paginate > strong").text)

                                time.sleep(2)
                                # 신청 취소
                                cancels[i].click()
                                time.sleep(2)

                                # 경고창 확인
                                result = driver.switch_to.alert
                                result.accept()
                                result.dismiss()

                                driver.switch_to.window(tabs[0])
                                time.sleep(0.5)
                                driver.switch_to.frame("papermain")

                                # 현재 페이지로 회귀
                                if t > 1:
                                    print("1페이지가 아님")
                                    time.sleep(1.5)
                                    a = driver.find_elements(By.CSS_SELECTOR, ".paginate > a")
                                    a[a_index-1].click()
                                    time.sleep(1.5)

                                # 요소들 새로고침
                                # 신청일 리스트
                                dates = driver.find_elements(By.CSS_SELECTOR, ".date")
                                # date의 text를 담아두는 리스트
                                date_list = []

                                for index in range(len(dates)):
                                    date_list.append(dates[index].text.replace(".", "-")[:-1])

                                # 신청한 사람 리스트
                                users = driver.find_elements(By.CSS_SELECTOR, ".nickname")

                                # 신청취소 버튼 리스트
                                cancels = driver.find_elements(By.CSS_SELECTOR, ".btn.btn5")

                                continue

                            # 최신글이 6개월이 안됨 = 활동중인 블로그 -> 삭제할 필요 없음
                            else:
                                print("활동중인 블로그 -> 유지")
                                self.textBrowser.append("활동중인 블로그 -> 유지\n")
                                QApplication.processEvents()

                                driver.close()
                                driver.switch_to.window(tabs[0])
                                time.sleep(2)
                                driver.switch_to.frame("papermain")
                                i += 1
                                continue
                
                self.textBrowser.append("\n모든 이웃관리 완료!\n")
                QApplication.processEvents()
        except:
            traceback_message = str(traceback.format_exc())
            self.textBrowser.append(traceback_message)
            self.textBrowser.append("\n* 오류가 발생했습니다.")
            QApplication.processEvents()
        
        return driver


            
    
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
