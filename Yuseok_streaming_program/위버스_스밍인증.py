from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import autoit
import pyautogui
import traceback


# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager


import os

login_dict = {"yss2356" : "235688"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "로그인.ui"
UI_PATH2 = "위버스_스밍.ui"

def change_date(date):

    # yyyy-mm-dd-hh-mm 형태 만들기

    date = str(date)
    date = date[date.find('('):]
    date = date.replace(', ', '-')
    date = date.replace('(', '')
    date = date.replace(')', '')

    year = date[:5]

    check = date.split('-')[1:]

    # 10 이하 숫자 앞에 0 붙이기

    for i in range(len(check)):
        if int(check[i]) < 10:
            check[i] = f'0{check[i]}'

    date = year + '-'.join(check)

    return date

file_paths = [0]
index = 1


class Maindialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH2), self)

        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.start_btn.clicked.connect(self.start)
        self.close_btn.clicked.connect(self.close)


        self.file_path_1.clicked.connect(self.path)
        self.file_path_2.clicked.connect(self.path)
        self.file_path_3.clicked.connect(self.path)
        self.file_path_4.clicked.connect(self.path)
        self.file_path_5.clicked.connect(self.path)
        self.file_path_6.clicked.connect(self.path)
        self.file_path_7.clicked.connect(self.path)
        self.file_path_8.clicked.connect(self.path)
        self.file_path_9.clicked.connect(self.path)
        self.file_path_10.clicked.connect(self.path)
        self.file_path_11.clicked.connect(self.path)
        self.file_path_12.clicked.connect(self.path)
        self.file_path_13.clicked.connect(self.path)
        self.file_path_14.clicked.connect(self.path)
        self.file_path_15.clicked.connect(self.path)
        self.file_path_16.clicked.connect(self.path)
        self.file_path_17.clicked.connect(self.path)
        self.file_path_18.clicked.connect(self.path)
        self.file_path_19.clicked.connect(self.path)
        self.file_path_20.clicked.connect(self.path)
        self.file_path_21.clicked.connect(self.path)
        self.file_path_22.clicked.connect(self.path)
        self.file_path_23.clicked.connect(self.path)
        self.file_path_24.clicked.connect(self.path)



    def path(self):
        global file_paths
        global index

        dirName = QFileDialog.getOpenFileName(self)[0].replace('/', '\\')

        if dirName == '':
            pass
        else:
            file_paths.append(dirName)
            
            stat = dirName.split('\\')
            eval("self.path_board_" + str(index)).setText(stat[-1])

            index += 1
        
        

    
    def start(self):
        self.textBrowser.setText("")
        self.textBrowser.append("실행중....")
        self.textBrowser.append("대기중...")
        QApplication.processEvents()

        group_name = self.group.text()
        input_id = self.id.text()
        input_pw = self.pw.text()

        global file_paths



        for i in range(1, 25):

            try:
            
                path = file_paths[i]

                
                t = eval('self.dateTimeEdit_' + str(i) + '.dateTime()')
                print(t)

                # 댓글 추출
                comment = eval('self.comment_' + str(i) + '.toPlainText()')
                print(comment)

                # 셋팅 시간 추출
                set_time = change_date(t)


                while 1:

                    # 현재 시간 연속 갱신
                    now = datetime.datetime.now()
                    now = now.strftime('%Y-%m-%d-%H-%M')

                    if set_time != now:
                        continue
                    else:
                        # 브라우저 꺼짐 방지
                        chrome_options = Options()
                        chrome_options.add_experimental_option("detach", True)

                        # 불필요한 에러 메시지 없애기
                        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

                        service = Service(executable_path=ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=chrome_options)

                        # 웹페이지 해당 주소 이동
                        driver.implicitly_wait(5)
                        driver.maximize_window()

                        driver.get(f"https://weverse.io/{group_name}/feed")
                        time.sleep(3)


                        # sign up 클릭
                        driver.find_element(By.CSS_SELECTOR, "#root > div.App > div > div.GlobalLayoutView_header__1UkFL > header > div > div.HeaderView_action__QDUUD > button").click()
                        time.sleep(2)

                        # 이메일 입력
                        driver.find_element(By.CSS_SELECTOR, "#__next > div > div.sc-8ab46e1a-2.eZEkTN > form > div > div.sc-ed52fcbe-8.eoxMAH > input").send_keys(input_id)
                        driver.find_element(By.CSS_SELECTOR, "#__next > div > div.sc-8ab46e1a-2.eZEkTN > div:nth-child(4) > button").click()

                        time.sleep(2)

                        # 비밀번호 입력
                        driver.find_element(By.CSS_SELECTOR, "#__next > div > div.sc-8ab46e1a-2.eZEkTN > div > form > div.sc-d0f94a43-0.bCrkf > div > div.sc-ed52fcbe-8.eoxMAH > input").send_keys(input_pw)

                        # 로그인 클릭
                        driver.find_element(By.CSS_SELECTOR, "#__next > div > div.sc-8ab46e1a-2.eZEkTN > div > form > div.sc-58a7e114-0.cqmXWr > button").click()

                        time.sleep(2)

                        try:
                            driver.find_element(By.CSS_SELECTOR, "#modal > div > div > div.ArtistBirthdayModalView_content_wrap__PExH4 > button").click()

                        except:
                            pass

                        time.sleep(1)

                        # 팝업창 제거

                        try:
                            driver.find_element(By.CSS_SELECTOR, ".BaseModalView_bottom_button__XNhOi").click()

                        except:
                            pass

                        # 댓글 입력 칸 제어
                        driver.find_element(By.CSS_SELECTOR, "#root > div.App > div > div.body > div.CommunityNavigationLayoutView_content__\+9zMw > div > div.FeedArtistLayoutView_content__k9va2 > div.FeedArtistLayoutView_main__r0yQj.FeedArtistLayoutView_feed__TRGAV > div.EditorInputView_editor_input_wrap__T1dmr > div.DivAsButtonView_div_as_button__jl7Xf.EditorInputView_input_button__qjPaD > div").click()

                        driver.find_element(By.CSS_SELECTOR, "#wevEditor").send_keys(comment)

                        # Hide from Artists 클릭

                        if self.hide_from_artist.isChecked():
                            driver.find_element(By.CSS_SELECTOR, "#editorWriteModal > div > div > div.EditorModalLayoutView_footer_area__PZcVo > div > div:nth-child(2) > div > label").click()
                            time.sleep(0.5)


                        try:
                            # 이미지 선택
                            driver.find_element(By.CSS_SELECTOR, "#editorWriteModal > div > div > div.EditorModalLayoutView_footer_area__PZcVo > div > div:nth-child(1) > div.EditorWriteModalFooterView_button_icon_wrap__9d1WL.-photo > label").send_keys(Keys.ENTER)
                            time.sleep(5)

                            # 이미지 선택

                            # Basic Window info 값 handle 변수에 저장
                            handle = "[CLASS:#32770; TITLE:열기]"
                            print("handle ~~")
                            time.sleep(1.5)
                                    
                            time.sleep(3)

                            # 사진 클릭시 나오는 윈도우 창에서 파일이름 경로값 전달
                            autoit.control_set_text(handle, "Edit1", path)

                            print("경로 전달")
                            
                            time.sleep(2)
                                    
                            # 사진 클릭시 나오는 윈도우 창에서 Button1 클릭
                            autoit.control_click(handle, "Button1")

                            time.sleep(3)

                        except:
                            traceback_message = str(traceback.format_exc())
                            self.textBrowser.append(traceback_message)
                            QApplication.processEvents()
                            return
                            
            



                        # 사진 선택 후 확인
                        driver.find_element(By.CSS_SELECTOR, "#editorAttachmentModal > div > div > div.content.EditorModalLayoutView_content__uVAFS > div > div > div > div.modal_action > button.confirm_button").click()
                        time.sleep(1.5)

                        # 등록 버튼 클릭
                        driver.find_element(By.CSS_SELECTOR, "#editorWriteModal > div > div > div.EditorModalLayoutView_footer_area__PZcVo > div > div:nth-child(2) > button").click()
                        time.sleep(1.5)

                        driver.quit()

                        self.textBrowser.append(f"\n{i}번째 자동화 성공!\n")
                        self.textBrowser.append("다음 시간까지 대기중...")
                        QApplication.processEvents()
                        break

            except:
                self.textBrowser.append("\n자동화를 실행하는 중 오류가 발생했습니다.\n빈칸을 빠짐없이 모두 입력했는지 혹은 인터넷 연결 상태를 확인해주세요.")
                QApplication.processEvents()
                return

        self.textBrowser.append("\n** 모든 자동화 완료!! **")
        QApplication.processEvents()

         



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


        if input_id in login_dict.keys():
            if input_pw == login_dict[input_id]:
                pyautogui.alert("로그인 성공")
                self.hide()
                # 두번째 창 연결
                mainwindow = Maindialog()
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


