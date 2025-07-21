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

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager



# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# 시크릿 모드
chrome_options.add_argument('--incognito')

service = Service(executable_path=ChromeDriverManager().install())

# pyqt 부분
import os

# 변경사항
# 로그인 접속 아이디 리스트
login_dict = {"" : ""}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "트래픽(영구제).ui"

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

        for i in range(input_traffic):

            driver = webdriver.Chrome(service=service, options=chrome_options)

            # 웹페이지 해당 주소 이동
            driver.implicitly_wait(5)
            driver.maximize_window()

            driver.get(f"https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&sm=mtb_jum&query={input_keyword}")
            time.sleep(1)

            # 찾으려는 블로그의 인덱스
            index = 0

            while 1:
                blog_names = driver.find_elements(By.CSS_SELECTOR, ".user_info > .name")
                blog_url = driver.find_elements(By.CSS_SELECTOR, ".title_link")
                print(f"\nblog_url 길이 {len(blog_url)}\n")
                print(f"\nblog_names 길이 {len(blog_names)}\n")
                print(f"현재 인덱스 : {index}")


                # 현재 바라보고 있는 페이지에 없을 경우
                if index == len(blog_names):
                    print("페이지에 없음")
                    # 다음 페이지 불러오기
                    blog_names[-1].send_keys(Keys.END)
                    time.sleep(2)
                    blog_url[-1].send_keys(Keys.CONTROL + "\n")
                    tabs = driver.window_handles
                    driver.switch_to.window(tabs[1])
                    driver.close()
                    driver.switch_to.window(tabs[0])
                    time.sleep(2)
                    blog_names = driver.find_elements(By.CSS_SELECTOR, ".user_info > .name")
                    blog_url = driver.find_elements(By.CSS_SELECTOR, ".title_link")
                    time.sleep(2)
                    if index == len(blog_names):
                        print("더 이상 없음.")
                        break

                else:
                    blog_name = blog_names[index].text.split("\n")[0]
                    if blog_name == input_blog_name:
                        break
                    else:
                        blog_names = driver.find_elements(By.CSS_SELECTOR, ".user_info > .name")
                        blog_url = driver.find_elements(By.CSS_SELECTOR, ".title_link")
                        print(f"인덱스 : {index}, {blog_url[index].text}, {blog_name}")
                        index += 1
                    


            # 찾은 블로그 게시글 들어가기
            blog_url = driver.find_elements(By.CSS_SELECTOR, ".title_link")
            print(index)
            blog_url[index].click()

            # 체류시간
            time.sleep(input_stay_time)
            driver.close()
            self.update.emit(i)

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
        input_keyword = self.keyword.text()
        input_blog_name = self.blog_name.text()
        input_stay_time = self.stay_time.value()
        self.input_traffic = self.traffic.value()

        self.second_thread = secondThread(input_keyword, input_blog_name, input_stay_time, self.input_traffic)
        self.second_thread.update.connect(self.update_status)
        self.second_thread.start()

    def update_status(self, i):
        self.status.setValue(round((i + 1) / self.input_traffic * 100))

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
