from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import os
import pyautogui
import time
import openai
import traceback
from PyQt5.QtCore import QSettings
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "이상민_외주.ui"

class Maindialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH), self)

        self.memo_dirName = ""


        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)

        self.memo.clicked.connect(self.memo_click)

        # 실행, 리셋, 종료 버튼 클릭
        self.start_btn.clicked.connect(self.start)
        self.reset_btn.clicked.connect(self.reset)
        self.close_btn.clicked.connect(self.exit)


        settings = QSettings("블로그", "이상민")
        self.key.setText(settings.value("key", ""))

        

    def start(self):

        # 유효성 검사
        # 챗지 버전 선택
        if self.gpt_free.isChecked() == False and self.gpt_4.isChecked() == False:
            pyautogui.alert("설정을 모두 입력하세요.")
            return
        
        # API 키
        if self.key.text() == "":
            pyautogui.alert("설정을 모두 입력하세요.")
            return
        
        if self.memo_dirName == "":
            pyautogui.alert("파일을 불러오지 않았습니다.")
            return
        
        

        # 진행 상황 초기화
        self.status.setText("")

        api_key = self.key.text()

        settings = QSettings("블로그", "이상민")
        settings.setValue("key", api_key)


        # 저장 경로 설정
        save_path = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)

        if save_path == "":
            pyautogui.alert("저장 경로를 설정해주세요.")
            return

        self.status.append("실행중....")
        QApplication.processEvents()


        # 체크박스 블로그 링크로 선택되었을 경우
        self.generate_memo(self.memo_dirName, save_path, api_key)


        
    def reset(self):
        self.memo_dirName = ""
        self.status.setText("")


    # 챗지 버전 선택
    def select_ver(self):
        if self.gpt_free.isChecked():
            return "gpt-3.5-turbo"
        
        if self.gpt_4.isChecked():
            return 'gpt-4'


            
            

            
    def generate_memo(self, path, save_path, api_key):
        
        try:

            # path = 메모장 파일의 경로
            # 메모장 읽어와서 블로그 주소 

            ver = self.select_ver()

            print(ver)

            # 파일 경로 설정
            file_path = path

            # 파일을 열고 내용을 읽어 리스트에 저장
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()

            # 각 줄의 개행 문자 제거 및 리스트에 저장
            titles = [line.strip() for line in content]

            print(titles)

            cnt = 1
        
            for title in titles:

                openai.api_key = api_key

                # 특수 문자 패턴 정의
                special_chars_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/]')

                # 입력 문자열에서 특수 문자를 삭제
                clean_string = re.sub(special_chars_pattern, '', title)

                f = open(f"{save_path}\{clean_string}.txt", 'w', encoding="UTF-8")
                self.status.append("원고 생성 중...")
                QApplication.processEvents()
                

                while 1:
                    try:
                        messages = []
                        messages.append({"role": "user", "content": f"{title}\n 위 내용으로 블로그 글 작성해줘, 유사문서에 걸리지 않게 치환해줘, 제목은 다르게 바꿔줘"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}")
                        break

                    except:
                        traceback_message = str(traceback.format_exc())
                        self.status.append(traceback_message)
                        self.status.append("\n*오류가 발생하여 10초 뒤 재시도합니다.*")
                        QApplication.processEvents()
                        time.sleep(10)
                        self.status.append("\n재시도 중...")
                        QApplication.processEvents()
                        continue

                f.close()
                
                self.status.append(f"\n{cnt}개 생성 완료.\n")
                QApplication.processEvents()
                cnt += 1
                

            self.status.append("** 모든 자동화 완료 **\n")
            QApplication.processEvents()
        
        except:
            traceback_message = str(traceback.format_exc())
            self.status.append(traceback_message)
            self.status.append("\n*해당 오류가 발생했습니다.\n관리자에게 문의하세요.*")
            QApplication.processEvents()





        
    # 클릭 이벤트
    def memo_click(self):
        # 블로그 링크 파일 불러오기
        memo_dirName = QFileDialog.getOpenFileName(self)[0].replace('/', '\\')

        if memo_dirName == "":
            pyautogui.alert("파일을 지정해주세요.")
        else:
            self.memo_dirName = memo_dirName



    def exit(self):
        sys.exit()


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = Maindialog()
main_dialog.show()

sys.exit(app.exec_())
