import openai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
import pyautogui
import sys
from datetime import datetime
import traceback
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QSettings


# pyqt 부분
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 변경사항
UI_PATH = "로그인.ui"
UI_PATH2 = "챗gpt(구독제).ui"

# 변경사항
# 유효기간 지정
limit = "2024-06-20"


# 변경사항
# 로그인 접속 아이디 리스트
login_dict = {"bangkh" : "alscjf77!"}


# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager



class secondThread(QThread):
    start_signal = pyqtSignal(str)
    update_textbrowser = pyqtSignal(str)
    update_status = pyqtSignal(str)


    def __init__(self, blogs_url, path, file_names, api):
        super().__init__() 

        self.blogs_url = blogs_url
        self.path = path
        self.file_names = file_names
        self.api = api
        
    def run(self):
        self.start_signal.emit("")
        self.generate_post(self.blogs_url, self.path, self.file_names, self.api)


    def generate_post(self, blogs_url, path, file_names, api):

        try:
        
            self.update_status.emit("생성중...")

            # 블로그들 리스트 불러오기
            complete = 0


            for blog_url in blogs_url:

                # 브라우저 꺼짐 방지
                chrome_options = Options()
                chrome_options.add_experimental_option("detach", True)


                # 불필요한 에러 메시지 없애기
                chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

                service = Service(executable_path=ChromeDriverManager().install())
                chrome_options.add_argument('--headless')

                # 웹페이지 해당 주소 이동
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.implicitly_wait(5)
                driver.maximize_window()

                driver.get(blog_url)

                # try~~
                try:
                    # iframe 안에 들어가기
                    driver.switch_to.frame("mainFrame")
                    print("iframe 들어옴")
                except:
                    print("iframe 없음")
                    pass

                # 본문 수집 태그
                if len(driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")) != 0:
                    posts = driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")
                    # 블로그 본문 담을 변수 생성
                    post_list = []

                    for post in posts:
                        # 줄바꿈 제거
                        post_list.append(post.text.replace("\n", ""))

                    while 1:
                        if '' in post_list:
                            post_list.remove('')
                        else:
                            break


                    # 제목 제거
                    del post_list[0]


                # 다른 태그인 경우
                else:
                    posts = driver.find_element(By.CSS_SELECTOR, "#viewTypeSelector").text
                    
                    post_list.append(posts.replace("\n", ''))

                    while 1:
                        if "" in post_list:
                            post_list.remove('')
                        else:
                            break


                self.update_status.emit("본문 수집 완료")

                # 변경사항
                openai.api_key = api

                index = 0
                mox = len(post_list) // 4  

                self.update_status.emit("본문 생성중...")
                self.update_status.emit("평균 약 3~4분 소요됩니다.\n수집된 양에 따라 약간의 차이가 있을 수 있습니다.")

                try_index = 0

                with open(rf"{path}\{file_names[complete]}.txt", 'w', encoding='UTF-8') as f:

                    while try_index < 4:

                        messages = []
                        if try_index == 3:
                            prompt = ''.join(post_list[index:])
                            print(prompt)
                            messages.append({"role": "user", "content": f"{prompt} \n 위 글을 재구성해줘"})
                            try:
                                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, timeout = 120)

                            except:
                                traceback_message = str(traceback.format_exc())
                                self.update_status.emit(traceback_message)
                                self.update_status.emit("\n* 오류가 발생했습니다. *\n10초 뒤 재시도 합니다.")
                                time.sleep(10)
                                self.update_status.emit("\n재시도 중...")
                                continue
                            else:
                                assistant_content = completion.choices[0].message["content"].strip()
                                f.write(f"{assistant_content}\n")
                                break
                            
                        prompt = ''.join(post_list[index : index + mox])
                        print(prompt)
                        index = index + mox
                        messages.append({"role": "user", "content": f"{prompt} \n 위 글을 재구성해줘"})

                        try:
                            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, timeout = 120)
                            
                        except:
                            traceback_message = str(traceback.format_exc())

                            self.update_status.emit(traceback_message)
                            self.update_status.emit("\n*오류가 발생하여 10초 뒤 재시도합니다.*")
                            time.sleep(10)
                            self.update_status.emit("재시도 중...")
                            continue
                    
                        else:
                            assistant_content = completion.choices[0].message["content"].strip()
                            f.write(f"{assistant_content}\n")
                            try_index += 1

                self.update_status.emit(f"{complete + 1}개 저장 완료...")
                self.update_status.emit("")


                # 글자수세기
                
                with open(rf"{path}\{file_names[complete]}.txt", encoding="UTF-8") as f:
                    s = f.read()
                    count = 0
                    for i in s:
                        if i == " " or i == "\n":
                            continue
                        else:
                            count += 1

                self.update_textbrowser.emit(f"{file_names[complete]} : {count}자")

                complete += 1

                driver.quit()


            self.update_status.emit("모든 자동화 프로그램 완료.")
        
        except:
            traceback_message = str(traceback.format_exc())
            self.update_status.emit(traceback_message)
            self.update_status.emit("\n* 오류가 발생했습니다.")

        


class second(QDialog):
    # 메인 프로그램 넣을 자리
    def __init__(self):
        # 유효기간 변수 불러오기

        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH2), self)

        self.limit_date.setText(f"프로그램 만료일 : {limit}")


        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.start_btn.clicked.connect(self.main)
        self.stop_btn.clicked.connect(self.stop)
        self.reset_btn.clicked.connect(self.reset)
        self.close_btn.clicked.connect(self.close)

        
        settings = QSettings("GPT2", "원고프로그램")
        self.api.setText(settings.value("api1", ""))
        

    def main(self):

        self.status.setText("")
        self.textBrowser.setText("")

        blogs_url = self.blogs_url.text().split(",")
        file_names = self.file_name.text().split(",")

        api = self.api.text()



        # 유효성 검사
        if len(blogs_url) != len(file_names) or self.blogs_url.text() == '' or self.file_name.text() == '' or self.api.text() == '':
            pyautogui.alert("빈칸 혹은 파일 이름을 모두 입력해주세요.")
            return 0   
        else:
            path = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)
            if path == '':
                pyautogui.alert("저장할 경로를 설정해주세요.")
            else:

                settings = QSettings("GPT2", "원고프로그램")
                settings.setValue("api1", api)

                self.second_thread = secondThread(blogs_url, path, file_names, api)
                self.second_thread.update_status.connect(self.update_status)
                self.second_thread.update_textbrowser.connect(self.update_textbrowser)
                self.second_thread.start()

    def update_status(self, string):
        self.status.append(f"{string}")

    def update_textbrowser(self, string):
        self.textBrowser.append(f"{string}")

    def stop(self):
        self.second_thread.terminate()
        self.status.append("\n*프로그램 중지*\n")
    

    
    def reset(self):
        self.blogs_url.setText("")
        self.file_name.setText("")
        self.status.setText("")
        self.textBrowser.setText("")

    def close(self):
        sys.exit()
                


class first(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH), self)

        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.login_btn.clicked.connect(self.login_start)
        self.close_btn.clicked.connect(self.close)

    def login_start(self):
        
        # 로그인 접속 아이디와 유효기간 변수 불러오기
        global login_dict

        input_id = self.id.text()
        input_pw = self.pw.text()

        now = datetime.now()

        if input_id in login_dict.keys():
            if input_pw == login_dict[input_id]:
                # 유효기간 만료
                if limit <= str(now.date()):
                    pyautogui.alert("유효기간이 만료되었습니다.\n관리자에게 문의하세요.")
                    return
                
                else:
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
        



QApplication.setStyle("fusion")
app = QApplication(sys.argv)
sub_windoww = first()
sub_windoww.show()

sys.exit(app.exec_())



