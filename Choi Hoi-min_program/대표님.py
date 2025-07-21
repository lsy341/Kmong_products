from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import os
import pyautogui
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import openai
import traceback

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
chrome_options.add_argument('--headless')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "블로그대행사_외주.ui"

class Maindialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH), self)

        self.url_dirName = ""
        self.link_dirName = ""

        self.generate_post.setVisible(False)
        self.label_7.setVisible(False)

        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.check_keyword.clicked.connect(self.keyword_click)
        self.check_blog_url.clicked.connect(self.blog_url_click)
        self.check_blog_link.clicked.connect(self.blog_link_click)


        self.blog_url.clicked.connect(self.url_click)
        self.blog_link.clicked.connect(self.link_click)

        # 실행, 리셋, 종료 버튼 클릭
        self.start_btn.clicked.connect(self.start)
        self.reset_btn.clicked.connect(self.reset)
        self.close_btn.clicked.connect(self.exit)
        
        # 초기에 버튼을 숨김
        self.keyword.setVisible(False)
        self.blog_url.setVisible(False)
        self.blog_link.setVisible(False)

    def start(self):

        # 유효성 검사
        # 챗지 버전 선택
        if self.gpt_free.isChecked() == False and self.gpt_16k.isChecked() == False and self.gpt_4.isChecked() == False:
            pyautogui.alert("설정을 모두 입력하세요.")
            return
        
        # API 키
        if self.key.text() == "":
            pyautogui.alert("설정을 모두 입력하세요.")
            return
        
        # 검색 옵션
        if self.check_keyword.isChecked() == False and self.check_blog_url.isChecked() == False and self.check_blog_link.isChecked() == False:
            pyautogui.alert("검색 옵션을 모두 입력하세요.")
            return
        
        # 생성 원고 수
        if self.generate_post.value() <= 0:
            if self.check_blog_link.isChecked():
                pass
            else:
                pyautogui.alert("설정을 모두 입력하세요.")
                return
        
        

        # 글자수, 진행 상황 초기화
        self.textBrowser.setText("")
        self.status.setText("")

        api_key = self.key.text()


        # 저장 경로 설정
        save_path = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)

        if save_path == "":
            pyautogui.alert("저장 경로를 설정해주세요.")
            return

        input_generate_post = self.generate_post.value()


        self.status.append("실행중....")
        QApplication.processEvents()

        # 체크박스 키워드가 선택되었을 경우
        if self.check_keyword.isChecked():
            input_keyword = self.keyword.text()
            self.generate_keyword(input_keyword, save_path, input_generate_post, api_key)

        # 체크박스 블로그 주소로 선택되었을 경우
        elif self.check_blog_url.isChecked():
            self.generate_blog_url(self.url_dirName, save_path, input_generate_post, api_key)
        
        # 체크박스 블로그 링크로 선택되었을 경우
        elif self.check_blog_link.isChecked():
            self.generate_blog_link(self.link_dirName, save_path, api_key)
        
        else:
            pyautogui.alert("")

    def reset(self):
        self.check_keyword.setChecked(False)
        self.check_blog_url.setChecked(False)
        self.check_blog_link.setChecked(False)
        self.generate_post.setValue(0)
        self.keyword.setText("")
        self.textBrowser.setText("")
        self.status.setText("")

        self.keyword.setVisible(False)
        self.blog_url.setVisible(False)
        self.blog_link.setVisible(False)
        self.generate_post.setVisible(False)
        self.label_7.setVisible(False)


    # 챗지 버전 선택
    def select_ver(self):
        if self.gpt_free.isChecked():
            return "gpt-3.5-turbo"
        
        if self.gpt_16k.isChecked():
            return "gpt-3.5-turbo-16k"
        
        if self.gpt_4.isChecked():
            return 'gpt-4'


    
    def generate_keyword(self, keyword, save_path, generate_post, api_key):

        ver = self.select_ver()
                
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 웹페이지 해당 주소 이동
        driver.implicitly_wait(5)
        driver.maximize_window()

        driver.get(f"https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_opt&query={keyword}&nso=")
        time.sleep(2)

        
        post_index = 0
        blog_list = driver.find_elements(By.CSS_SELECTOR, '.title_link')
        time.sleep(1)
        random.shuffle(blog_list)

        # objec_cnt == generate_post
        objec_cnt = generate_post
        print(len(blog_list))
        post_cnt = 0

        save_index = len(blog_list)

        while post_cnt < objec_cnt:

            # 현재 날짜와 시간을 얻기
            today = datetime.now()

            # 날짜를 원하는 형식으로 포맷팅
            formatted_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식으로 출력

            today = formatted_date.split('-')
            today = ''.join(today)
            today = today[2:]


            # 현재 시간을 얻기
            current_time = datetime.now()

            # 시간을 원하는 형식으로 포맷팅 (시분초)
            current_time = current_time.strftime("%H%M%S")  # HHMMSS 형식으로 출력

            # 리스트 새로고침
            if post_index == len(blog_list):

                blog_list = driver.find_elements(By.CSS_SELECTOR, '.title_link')[save_index:]
                save_index += len(blog_list)
                random.shuffle(blog_list)

                # 더 이상 블로그가 없는 경우
                if len(blog_list) == 0:
                    self.status.append("더 이상 블로그가 없습니다.")
                    QApplication.processEvents()
                    return
                
                post_index = 0
                continue

            print(blog_list)
            print(len(blog_list))

            # 블로그 새 창으로 열기
            blog_list[post_index].send_keys(Keys.CONTROL, "\n")
            taps = driver.window_handles
            driver.switch_to.window(taps[1])

            current_link = driver.current_url
            
            time.sleep(1)

            # 여기서부터 시작

            self.status.append("본문 수집 중....")
            QApplication.processEvents()

            # 챗gpt 통해 본문 수집
            # iframe 안에 들어가기
            try:
                driver.switch_to.frame("mainFrame")
                print("frame 안으로 들어감")
            except:
                pass
                print("frame 없음")


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

                driver.close()
                # 메인 탭 전환
                driver.switch_to.window(taps[0])
                post_index += 1

                title = post_list[0]


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

                driver.close()
                # 메인 탭 전환
                driver.switch_to.window(taps[0])
                post_index += 1



            self.status.append("본문 수집 완료!")
            QApplication.processEvents()


            print(post_list)
            time.sleep(1)


            openai.api_key = api_key

            index = 0
            mox = len(post_list) // 4

            f = open(rf"{save_path}\[대표님]_{today}_{keyword}_{current_time}.txt", 'w', encoding="UTF-8")

            f.write(f"{current_link}\n{title}\n\n")

            self.status.append("원고 생성 중...")
            QApplication.processEvents()

            try_index = 0

            while try_index < 4:
                try:
                    messages = []
                    if try_index == 3:
                        prompt = ''.join(post_list[index:])
                        messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n\n")
                        break
                    prompt = ''.join(post_list[index : index + mox])
                    index = index + mox
                    messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                    completion = openai.ChatCompletion.create(model=ver, messages=messages)
                    assistant_content = completion.choices[0].message["content"].strip()
                    print(assistant_content)
                    f.write(f"{assistant_content}\n")
                    try_index += 1

                except:
                    traceback_message = str(traceback.format_exc())
                    self.status.append(traceback_message)
                    self.status.append("\n*오류가 발생하여 1분 뒤 재시도합니다.*")
                    QApplication.processEvents()
                    time.sleep(60)
                    self.status.append("재시도 중...")
                    QApplication.processEvents()
                    continue

            f.close()

            post_cnt += 1

            self.status.append(f"\n{post_cnt}개 생성 완료.\n")
            QApplication.processEvents()

            # 글자수세기

            f = open(rf"{save_path}\[대표님]_{today}_{keyword}_{current_time}.txt", encoding="UTF-8")
            s = f.read()
            count = 0
            for i in s:
                if i == " " or i == "\n":
                    continue
                else:
                    count += 1
            
            self.textBrowser.append(f"{today}_{keyword}_{current_time} : {count}자")
            QApplication.processEvents()
            

        self.status.append("** 모든 자동화 완료 **\n")
        QApplication.processEvents()

            
            
            





            


            

    def generate_blog_url(self, path, save_path, generate_post, api_key):
        # path = 메모장 파일의 경로
        # 메모장 읽어와서 블로그 주소 

        ver = self.select_ver()

        # 파일 경로 설정
        file_path = path

        # 파일을 열고 내용을 읽어 리스트에 저장
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # 각 줄의 개행 문자 제거 및 리스트에 저장
        blog_urls = [line.strip() for line in content]
        random.shuffle(blog_urls)

        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 웹페이지 해당 주소 이동
        driver.implicitly_wait(5)
        driver.maximize_window()
        time.sleep(1)

        for url in blog_urls:

            print(url)

            # url 모바일로 변경
            url = url[:8] + "m." + url[8:]

            print(url)

            # 블로그 메인 화면 접속
            driver.get(url)
            time.sleep(1)


            # 블로그 정렬
            try:
                driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button.btn__xjUPw.is_active__iSUFY").click()
            except:
                pass

            # 슬라이싱 할 변수 + 0번째부터 마지막 인덱스까지
            post_index = 0  

            # post_index를 기억해줄 변수
            save_index = 0
            blog_list = driver.find_elements(By.CSS_SELECTOR, '.link__iGhdI')

            # 블로그 리스트 -> 이중 리스트 [(인덱스, 블로그 주소), ....]
            blog_list = list(enumerate(blog_list)) 
            random.shuffle(blog_list)

            blog_dates = driver.find_elements(By.CSS_SELECTOR, ".time__MHDWV")
            blog_dates = list(enumerate(blog_dates))


            # 반복문 돌 때 마다 카운트
            generate_cnt = 0

            while generate_cnt < generate_post:

                # 수집할 블로그가 더 남아있는 경우
                if len(blog_list) == post_index:
                    print("수집할 블로그 남음")
                    save_index += post_index
                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".link__iGhdI")[save_index:]

                    # 더 이상 블로그가 없는 경우
                    if len(blog_list) == 0:
                        self.status.append("더 이상 블로그가 없습니다.")
                        QApplication.processEvents()
                        return
                    
                    blog_list = list(enumerate(blog_list))
                    random.shuffle(blog_list)

                    blog_dates = driver.find_elements(By.CSS_SELECTOR, ".time__MHDWV")[save_index:]
                    blog_dates = list(enumerate(blog_dates))
                    post_index = 0


                # 블로그 주소 새 창으로 접속
                blog_list[post_index][1].send_keys(Keys.CONTROL, '\n')

                # 해당 게시물의 등록일자
                date = blog_dates[blog_list[post_index][0]][1].text

                # 등록일자 변수
                date = date.replace(". ", "_")

                # 탭 변경
                taps = driver.window_handles
                driver.switch_to.window(taps[1])

                current_link = driver.current_url

                # 포스팅 마지막 주소
                current_url = driver.current_url
                last_url = current_url.split('/')
                idx = last_url[3].find('N')
                if idx == -1:
                    last_url = last_url[4]
                else:
                    last_url = last_url[3][idx + 3 : idx + 15]

                # 현재 날짜 얻기
                today = datetime.now()

                # 날짜를 원하는 형식으로 포맷팅
                formatted_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식

                today = formatted_date.split('-')
                today = ''.join(today)
                today = today[2:]
                

                self.status.append("본문 수집 중....")
                QApplication.processEvents()

                # 블로그 본문 추출
                # iframe 접속
                try:
                    driver.switch_to.frame("mainFrame")
                    print("frame 안으로 들어감")
                except:
                    pass
                    print("frame 없음")

                post_list = []

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

                    driver.close()
                    # 메인 탭 전환
                    driver.switch_to.window(taps[0])
                    post_index += 1

                    title = post_list[0]


                    # 제목 제거
                    del post_list[0]
                    print(post_list) 

                # 체크사항
                # 다른 태그인 경우
                else:
                    posts = driver.find_element(By.CSS_SELECTOR, "#viewTypeSelector").text
                    
                    post_list.append(posts.replace("\n", ''))

                    while 1:
                        if "" in post_list:
                            post_list.remove('')
                        else:
                            break

                    driver.close()
                    # 메인 탭 전환
                    driver.switch_to.window(taps[0])
                    post_index += 1

                    print(post_list)



                self.status.append("본문 수집 완료!")
                QApplication.processEvents()




                openai.api_key = api_key

                index = 0
                mox = len(post_list) // 4

                f = open(rf"{save_path}\[대표님]_{today}_{date}_{last_url}.txt", 'w', encoding="UTF-8")

                f.write(f"{current_link}\n{title}\n\n")

                self.status.append("원고 생성 중...")
                QApplication.processEvents()

                try_index = 0

                while try_index < 4:
                    try:
                        messages = []
                        if try_index == 3:
                            prompt = ''.join(post_list[index:])
                            messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                            completion = openai.ChatCompletion.create(model=ver, messages=messages)
                            assistant_content = completion.choices[0].message["content"].strip()
                            print(assistant_content)
                            f.write(f"{assistant_content}\n\n")
                            break
                        prompt = ''.join(post_list[index : index + mox])
                        index = index + mox
                        messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n")
                        try_index += 1

                    except:
                        traceback_message = str(traceback.format_exc())
                        self.status.append(traceback_message)
                        self.status.append("\n*오류가 발생하여 1분 뒤 재시도합니다.*")
                        QApplication.processEvents()
                        time.sleep(60)
                        self.status.append("재시도 중...")
                        QApplication.processEvents()
                        continue

                f.close()

                
                generate_cnt += 1
                self.status.append(f"\n{generate_cnt}개 생성 완료.\n")
                QApplication.processEvents()


                # 글자수세기

                f = open(rf"{save_path}\[대표님]_{today}_{date}_{last_url}.txt", encoding="UTF-8")
                s = f.read()
                count = 0
                for i in s:
                    if i == " " or i == "\n":
                        continue
                    else:
                        count += 1
                
                self.textBrowser.append(f"{today}_{date}_{last_url} : {count}자")
                QApplication.processEvents()

                
             


        self.status.append("** 모든 자동화 완료 **\n")
        QApplication.processEvents()


            
    def generate_blog_link(self, path, save_path, api_key):
        # path = 메모장 파일의 경로
        # 메모장 읽어와서 블로그 주소 

        ver = self.select_ver()

        # 파일 경로 설정
        file_path = path

        # 파일을 열고 내용을 읽어 리스트에 저장
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # 각 줄의 개행 문자 제거 및 리스트에 저장
        blog_links = [line.strip() for line in content]
        random.shuffle(blog_links)

        cnt = 1
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
        # 웹페이지 해당 주소 이동
        driver.implicitly_wait(5)
        driver.maximize_window()

        for link in blog_links:



            # 블로그 메인 화면 접속
            driver.get(link)
            time.sleep(1)

            # 블로그 이름 추출
            # iframe 접속
            try:
                driver.switch_to.frame("mainFrame")
                print("iframe 접속")
            except:
                print("iframe 없음")
                pass

            

            current_link = driver.current_url


            # 포스팅 마지막 주소 추출
            current_url = driver.current_url
            last_url = current_url.split('/')
            
            # 블로그 링크가 이상한 경우 https://blog.naver.com/PostView.naver?blogId=hi_rent87&logNo=223238312812&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=1&postListTopCurrentPage=&from=
            if len(last_url) == 4:
                idx = last_url[3].find("No=")
                if idx == -1:
                    end_url = last_url[3]
                else:
                    end_url = last_url[3][idx + 3 : idx + 15]

                # 블로그 아이디 찾기
                blog_id_idx = last_url[3].find("Id=")
                blog_id_end_idx = last_url[3].find("&")

                if blog_id_idx == -1:
                    blog_id = last_url[3][:blog_id_end_idx]
                else:
                    blog_id = last_url[3][blog_id_idx + 3 : blog_id_end_idx]

            # 블로그 링크가 아름다운 경우 https://blog.naver.com/hi_rent87/223242255704
            else:
                idx = last_url[4].find('?')
                if idx == -1:
                    end_url = last_url[4]
                else:
                    end_url = last_url[4][:idx]

                # 블로그 아이디 찾기
                blog_id = last_url[3]

            print(blog_id)

            print(end_url)


            
            # 현재 날짜 얻기
            today = datetime.now()

            # 날짜를 원하는 형식으로 포맷팅
            formatted_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD 형식

            today = formatted_date.split('-')
            today = ''.join(today)
            today = today[2:]


            
            self.status.append("본문 수집 중....")
            QApplication.processEvents()

            # 블로그 본문 담을 변수 생성
            post_list = []

            if len(driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")) != 0:

                # 챗gpt 통해 본문 수집
                # 본문 수집
                posts = driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")

                for post in posts:
                    # 줄바꿈 제거
                    post_list.append(post.text.replace("\n", ""))

                while 1:
                    if '' in post_list:
                        post_list.remove('')
                    else:
                        break

                title = post_list[0]

                del post_list[0]

            else:

                # 다른 태그인 경우
                posts = driver.find_element(By.CSS_SELECTOR, "#postViewArea").text
                
                post_list.append(posts.replace("\n", ''))

                while 1:
                    if "" in post_list:
                        post_list.remove('')
                    else:
                        break


            
            print(post_list)

            self.status.append("본문 수집 완료!")
            QApplication.processEvents()

            openai.api_key = api_key

            index = 0
            mox = len(post_list) // 4

            f = open(rf"{save_path}\[대표님]_{today}_{blog_id}_{end_url}.txt", 'w', encoding="UTF-8")

            f.write(f"{current_link}\n{title}\n\n")

            self.status.append("원고 생성 중...")
            QApplication.processEvents()
            
            try_index = 0

            while try_index < 4:
                try:
                    messages = []
                    if try_index == 3:
                        prompt = ''.join(post_list[index:])
                        messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n\n")
                        break
                    prompt = ''.join(post_list[index : index + mox])
                    index = index + mox
                    messages.append({"role": "user", "content": f"아래 내용에 있는 단어 및 어휘를 모두 치환하고 문장 순서를 변경 후 원본 내용과 중복되지 않도록 자연스럽게 작성해줘.\n{prompt}"})
                    completion = openai.ChatCompletion.create(model=ver, messages=messages)
                    assistant_content = completion.choices[0].message["content"].strip()
                    print(assistant_content)
                    f.write(f"{assistant_content}\n")
                    try_index += 1

                except:
                    traceback_message = str(traceback.format_exc())
                    self.status.append(traceback_message)
                    self.status.append("\n*오류가 발생하여 1분 뒤 재시도합니다.*")
                    QApplication.processEvents()
                    time.sleep(60)
                    self.status.append("재시도 중...")
                    QApplication.processEvents()
                    continue

            f.close()
            
            self.status.append(f"\n{cnt}개 생성 완료.\n")
            QApplication.processEvents()
            cnt += 1

            # 글자수세기

            f = open(rf"{save_path}\[대표님]_{today}_{blog_id}_{end_url}.txt", encoding="UTF-8")
            s = f.read()
            count = 0
            for i in s:
                if i == " " or i == "\n":
                    continue
                else:
                    count += 1

            self.textBrowser.append(f"{today}_{blog_id}_{end_url} : {count}자")
            QApplication.processEvents()
            

        self.status.append("** 모든 자동화 완료 **\n")
        QApplication.processEvents()



        

    # 클릭 이벤트
    def url_click(self):
        # 블로그 주소 파일 불러오기
        url_dirName = QFileDialog.getOpenFileName(self)[0].replace('/', '\\')

        if url_dirName == "":
            pyautogui.alert("파일을 지정해주세요.")
        else:
            self.url_dirName = url_dirName
        
    def link_click(self):
        # 블로그 링크 파일 불러오기
        link_dirName = QFileDialog.getOpenFileName(self)[0].replace('/', '\\')

        if link_dirName == "":
            pyautogui.alert("파일을 지정해주세요.")
        else:
            self.link_dirName = link_dirName


    
    def keyword_click(self):
        if self.check_keyword.isChecked():
            self.keyword.setVisible(True)
            self.generate_post.setVisible(True)
            self.label_7.setVisible(True)

            self.blog_url.setVisible(False)
            self.blog_link.setVisible(False)

            self.check_blog_url.setChecked(False)
            self.check_blog_link.setChecked(False)
            
        else:
            self.keyword.setVisible(False)
            self.generate_post.setVisible(False)
            self.label_7.setVisible(False)

    def blog_url_click(self):
        if self.check_blog_url.isChecked():
            self.blog_url.setVisible(True)
            self.generate_post.setVisible(True)
            self.label_7.setVisible(True)

            self.keyword.setVisible(False)
            self.blog_link.setVisible(False)

            self.check_keyword.setChecked(False)
            self.check_blog_link.setChecked(False)

        else:
            self.blog_url.setVisible(False)
            self.generate_post.setVisible(False)
            self.label_7.setVisible(False)

    def blog_link_click(self):
        if self.check_blog_link.isChecked():
            self.blog_link.setVisible(True)

            self.generate_post.setVisible(False)
            self.keyword.setVisible(False)
            self.blog_url.setVisible(False)

            self.check_keyword.setChecked(False)
            self.check_blog_url.setChecked(False)

        else:
            self.blog_link.setVisible(False)


    def exit(self):
        sys.exit()


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = Maindialog()
main_dialog.show()

sys.exit(app.exec_())
