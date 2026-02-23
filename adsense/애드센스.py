from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
import sys
import os
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import openai
import traceback
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

# 크롬 드라이버 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = "애드센스.ui"

class secondThread(QThread):
    start_signal = pyqtSignal(str)
    update_textbrowser = pyqtSignal(str)
    update_status = pyqtSignal(str)

    def __init__(self, ver, input_keyword, url_dirName, link_dirName, save_path, input_generate_post, api_key, post_blog, ID, PW, tstory_num):
        super().__init__()

        self.input_keyword = input_keyword
        self.url_dirName = url_dirName
        self.link_dirName = link_dirName
        self.save_path = save_path
        self.input_generate_post = input_generate_post
        self.api_key = api_key
        self.post_blog = post_blog
        self.ID = ID
        self.PW = PW
        self.tstory_num = tstory_num

        self.check_keyword = 0
        self.check_url = 0
        self.check_link = 0

        self.ver = ver

        
    def run(self):

        self.start_signal.emit("")

        try:

            if self.check_keyword == 1:
                self.generate_keyword(self.ver, self.input_keyword, self.save_path, self.input_generate_post, self.api_key)
            
            elif self.check_url == 1:
                self.generate_blog_url(self.ver, self.url_dirName, self.save_path, self.input_generate_post, self.api_key)

            elif self.check_link == 1:
                self.generate_blog_link(self.ver, self.link_dirName, self.save_path, self.api_key)

        except:
            traceback_message = str(traceback.format_exc())
            self.update_status.emit(traceback_message)





    def generate_keyword(self, ver, keyword, save_path, generate_post, api_key):


        self.start_signal.emit("")
        
        post_index = 0

        # objec_cnt == generate_post
        objec_cnt = generate_post
        
        post_cnt = 0

        

        while post_cnt < objec_cnt:

            # 브라우저 꺼짐 방지
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)

            # 불필요한 에러 메시지 없애기
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            service = Service(executable_path=ChromeDriverManager().install())
            chrome_options.add_argument('--headless')

            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 웹페이지 해당 주소 이동
            self.driver.implicitly_wait(5)
            self.driver.maximize_window()

            self.driver.get(f"https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_opt&query={keyword}&nso=")
            time.sleep(2)

            blog_list = self.driver.find_elements(By.CSS_SELECTOR, '.title_link')
            time.sleep(1)
            print(len(blog_list))

            save_index = len(blog_list)

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

            print(post_index)
            print(len(blog_list))

            # 리스트 새로고침
            if post_index >= len(blog_list):

                old_blog_list = blog_list

                print(save_index)

                for f in range(post_index//13):
                    blog_list[-3].send_keys(Keys.END)
                    time.sleep(2)

                blog_list = self.driver.find_elements(By.CSS_SELECTOR, '.title_link')
                save_index += len(blog_list)

                # 더 이상 블로그가 없는 경우
                if len(blog_list) == len(old_blog_list):
                    self.update_status.emit("더 이상 블로그가 없습니다.")
                    return
                
                

            print(len(blog_list))
            print(post_index)

            # 블로그 새 창으로 열기
            blog_list[post_index].send_keys(Keys.CONTROL, "\n")
            taps = self.driver.window_handles
            self.driver.switch_to.window(taps[1])

            current_link = self.driver.current_url
            
            time.sleep(1)

            # 여기서부터 시작

            self.update_status.emit("본문 수집 중....")

            # 챗gpt 통해 본문 수집
            # iframe 안에 들어가기
            try:
                self.driver.switch_to.frame("mainFrame")
                print("frame 안으로 들어감")
            except:
                pass
                print("frame 없음")

            # 블로그 본문 담을 변수 생성
            post_list = []

            # 본문 수집 태그
            if len(self.driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")) != 0:
                posts = self.driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")


                for post in posts:
                    # 줄바꿈 제거
                    post_list.append(post.text.replace("\n", ""))

                while 1:
                    if '' in post_list:
                        post_list.remove('')
                    else:
                        break

                self.driver.close()
                # 메인 탭 전환
                self.driver.switch_to.window(taps[0])
                post_index += 1

                title = post_list[0]

                # 제목 제거
                del post_list[0]




            # 다른 태그인 경우
            else:
                posts = self.driver.find_element(By.CSS_SELECTOR, "#viewTypeSelector").text
                
                post_list.append(posts.replace("\n", ''))

                while 1:
                    if "" in post_list:
                        post_list.remove('')
                    else:
                        break

                self.driver.close()
                # 메인 탭 전환
                self.driver.switch_to.window(taps[0])
                post_index += 1


            self.update_status.emit("본문 수집 완료!")

            self.driver.quit()


            # print(post_list)
            time.sleep(1)


            openai.api_key = api_key

            index = 0
            mox = len(post_list) // 4

            post_save_path = rf"{save_path}\{today}_{keyword}_{current_time}.txt"

            self.update_status.emit("원고 생성 중...")

            f = open(post_save_path, 'w', encoding="UTF-8")

            f.write(f"{current_link}\n{title}\n\n")

            try_index = 0

            while try_index < 4:
                try:
                    messages = []
                    if try_index == 3:
                        prompt = ''.join(post_list[index:])
                        messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n\n")
                        break
                    prompt = ''.join(post_list[index : index + mox])
                    index = index + mox
                    messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                    completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                    assistant_content = completion.choices[0].message["content"].strip()
                    print(assistant_content)
                    f.write(f"{assistant_content}\n")
                    try_index += 1
                    

                except:
                    traceback_message = str(traceback.format_exc())
                    self.update_status.emit(traceback_message)
                    self.update_status.emit("\n*오류가 발생하여 10초 뒤 재시도합니다.*")
                    time.sleep(10)
                    self.update_status.emit("재시도 중...")
                    continue

            f.close()


            post_cnt += 1

            self.update_status.emit(f"\n{post_cnt}개 생성 완료.\n")

            
            # 글자수세기

            f = open(post_save_path, 'r', encoding="UTF-8")
            count = 0

            number = ''.join(f.readlines()[2:])

            for i in number:
                if i == " " or i == "\n":
                    continue
                else:
                    count += 1

            f.close()

            self.update_textbrowser.emit(f"{today}_{keyword}_{current_time} : {count}자")

            self.update_status.emit("포스팅 임시저장 중....")

            print(f"어디로 포스팅? {self.post_blog}")

            if self.post_blog == 1:
                self.naver_post(post_cnt, post_save_path)
            
            elif self.post_blog == 2:
                self.tstory_post(post_cnt, post_save_path)
                pass

            elif self.post_blog == 3:
                self.kakao_post(post_cnt, post_save_path)


            
        
        self.update_status.emit("** 모든 자동화 완료 **\n")



    def generate_blog_url(self, ver, path, save_path, generate_post, api_key):
        # path = 메모장 파일의 경로
        # 메모장 읽어와서 블로그 주소 

        print(ver)

        # 파일 경로 설정
        file_path = path

        # 파일을 열고 내용을 읽어 리스트에 저장
        file = open(file_path, 'r', encoding='UTF-8')
        content = file.readlines()
        file.close()

        # 각 줄의 개행 문자 제거 및 리스트에 저장
        blog_urls = [line.strip() for line in content]

        for url in blog_urls:
            print(url)

            # url 모바일로 변경
            url = url[:8] + "m." + url[8:]

            print(url)


            # 슬라이싱 할 변수 + 0번째부터 마지막 인덱스까지
            post_index = 0  

            # post_index를 기억해줄 변수
            save_index = 0


            # 반복문 돌 때 마다 카운트
            generate_cnt = 0

            while generate_cnt < generate_post:

                # 브라우저 꺼짐 방지
                chrome_options = Options()
                chrome_options.add_experimental_option("detach", True)

                # 불필요한 에러 메시지 없애기
                chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

                service = Service(executable_path=ChromeDriverManager().install())
                chrome_options.add_argument('--headless')
                    
                driver = webdriver.Chrome(service=service, options=chrome_options)

                # 웹페이지 해당 주소 이동
                driver.implicitly_wait(5)
                driver.maximize_window()
                time.sleep(1)

                # 블로그 메인 화면 접속
                driver.get(url)
                time.sleep(1)

                # 블로그 정렬
                try:
                    driver.find_element(By.CSS_SELECTOR, "#postlist_block > div.post_block__Q6T_o > div > div > button.btn__xjUPw.is_active__iSUFY").click()
                except:
                    pass

                # 블로그 리스트
                blog_list = driver.find_elements(By.CSS_SELECTOR, '.link__iGhdI')
                

                # 수집할 블로그가 더 남아있는 경우
                if post_index >= len(blog_list):

                    print("수집할 블로그 남음")

                    for f in range(post_index//20):
                        blog_list[-3].send_keys(Keys.END)
                        time.sleep(2.5)

                    blog_list = driver.find_elements(By.CSS_SELECTOR, ".link__iGhdI")
                    save_index += post_index

                    # 더 이상 블로그가 없는 경우
                    if len(blog_list) == 0:
                        self.update_status.emit("더 이상 블로그가 없습니다.")
                        return


                # 블로그 주소 새 창으로 접속
                blog_list[post_index].send_keys(Keys.ENTER)

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
                

                self.update_status.emit("본문 수집 중....")

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
                    

                    driver.quit()

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

                    driver.quit()

                    post_index += 1

                    print(post_list)


                self.update_status.emit("본문 수집 완료!")




                openai.api_key = api_key

                index = 0
                mox = len(post_list) // 4

                post_save_path = rf"{save_path}\{today}_{last_url}.txt"

                f= open(post_save_path, 'w', encoding="UTF-8")
                f.write(f"{current_link}\n{title}\n\n")

                self.update_status.emit("원고 생성 중...")

                try_index = 0

                while try_index < 4:
                    try:
                        messages = []
                        if try_index == 3:
                            prompt = ''.join(post_list[index:])
                            messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                            completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                            assistant_content = completion.choices[0].message["content"].strip()
                            print(assistant_content)
                            f.write(f"{assistant_content}\n\n")
                            break
                        prompt = ''.join(post_list[index : index + mox])
                        index = index + mox
                        messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n")
                        try_index += 1

                    except:
                        traceback_message = str(traceback.format_exc())
                        self.update_status.emit(traceback_message)
                        self.update_status.emit("\n*오류가 발생하여 10초 뒤 재시도합니다.*")
                        time.sleep(10)

                        self.update_status.emit("재시도 중...")
                        continue

                f.close()


                
                generate_cnt += 1

                self.update_status.emit(f"\n{generate_cnt}개 생성 완료.\n")


                # 글자수세기

                f = open(post_save_path, 'r', encoding="UTF-8")
                count = 0

                number = ''.join(f.readlines()[2:])

                for i in number:
                    if i == " " or i == "\n":
                        continue
                    else:
                        count += 1

                f.close()

                        
                self.update_textbrowser.emit(f"{today}_{last_url} : {count}자")

                if self.post_blog == 1:
                    self.naver_post(generate_cnt, post_save_path)

                elif self.post_blog == 2:
                    self.tstory_post(generate_cnt, post_save_path)

                elif self.post_blog == 3:
                    self.kakao_post(generate_cnt, post_save_path)

                
             

        self.update_status.emit("** 모든 자동화 완료 **\n")
        



    def generate_blog_link(self, ver, path, save_path, api_key):
        # path = 메모장 파일의 경로
        # 메모장 읽어와서 블로그 주소 

        print(ver)

        # 파일 경로 설정
        file_path = path

        # 파일을 열고 내용을 읽어 리스트에 저장
        file = open(file_path, 'r', encoding='utf-8')
        content = file.readlines()
        file.close()

        # 각 줄의 개행 문자 제거 및 리스트에 저장
        blog_links = [line.strip() for line in content]

        cnt = 1
        

        for link in blog_links:

            # 브라우저 꺼짐 방지
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)

            # 불필요한 에러 메시지 없애기
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            service = Service(executable_path=ChromeDriverManager().install())
            chrome_options.add_argument('--headless')

            driver = webdriver.Chrome(service=service, options=chrome_options)
    
            # 웹페이지 해당 주소 이동
            driver.implicitly_wait(5)
            driver.maximize_window()


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


            self.update_status.emit("본문 수집 중....")

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

            self.update_status.emit("본문 수집 완료!")

            driver.quit()

            openai.api_key = api_key

            index = 0
            mox = len(post_list) // 4

            post_save_path = rf"{save_path}\{today}_{blog_id}_{end_url}.txt"

            f = open(post_save_path, 'w', encoding="UTF-8")
            f.write(f"{current_link}\n{title}\n\n")

            self.update_status.emit("원고 생성 중...")

            try_index = 0

            while try_index < 4:
                try:
                    messages = []
                    if try_index == 3:
                        prompt = ''.join(post_list[index:])
                        messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                        completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                        assistant_content = completion.choices[0].message["content"].strip()
                        print(assistant_content)
                        f.write(f"{assistant_content}\n\n")
                        break
                    prompt = ''.join(post_list[index : index + mox])
                    index = index + mox
                    messages.append({"role": "user", "content": f"{prompt}\n 위 내용을 재구성해줘"})
                    completion = openai.ChatCompletion.create(model=ver, messages=messages, timeout = 120)
                    assistant_content = completion.choices[0].message["content"].strip()
                    print(assistant_content)
                    f.write(f"{assistant_content}\n")
                    try_index += 1


                except:
                    traceback_message = str(traceback.format_exc())
                    self.update_status.emit(traceback_message)
                    self.update_status.emit("\n*오류가 발생하여 10초 뒤 재시도합니다.*")
                    time.sleep(10)

                    self.update_status.emit("재시도 중...")
                    continue

            f.close()


            self.update_status.emit(f"\n{cnt}개 생성 완료.\n")

            cnt += 1

            # 글자수세기

            f = open(post_save_path, 'r', encoding="UTF-8")
            count = 0

            number = ''.join(f.readlines()[2:])

            for i in number:
                if i == " " or i == "\n":
                    continue
                else:
                    count += 1

            f.close()

            self.update_textbrowser.emit(f"{today}_{blog_id}_{end_url} : {count}자")

            if self.post_blog == 1:
                self.naver_post(cnt - 1, post_save_path)

            elif self.post_blog == 2:
                self.tstory_post(cnt - 1, post_save_path)

            elif self.post_blog == 3:
                self.kakao_post(cnt - 1, post_save_path)


        self.update_status.emit("** 모든 자동화 완료 **\n")





    
    def tstory_post(self, post_cnt, post_save_path):

        chrome_options2 = Options()
        chrome_options2.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options2.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(executable_path=ChromeDriverManager().install())

        # 포스팅 작업
        browser = webdriver.Chrome(service=service, options=chrome_options2)

        url = "https://www.tistory.com/auth/login"

        # 웹페이지 해당 주소 이동
        browser.implicitly_wait(5)
        browser.maximize_window()
        browser.get(url)

        time.sleep(3)

        # 티스토리 계정으로 로그인
        browser.find_element(By.CSS_SELECTOR, ".btn_login.link_tistory_id").click()
        time.sleep(2)

        # 아이디, 비밀번호 입력
        browser.find_element(By.CSS_SELECTOR, "#loginId").send_keys(self.ID)
        browser.find_element(By.CSS_SELECTOR, "#loginPw").send_keys(self.PW)

        time.sleep(1)

        # 로그인 버튼 클릭
        browser.find_element(By.CSS_SELECTOR, ".btn_login").click()
        time.sleep(1.5)


        # 프로필 클릭
        browser.find_element(By.CSS_SELECTOR, ".link_profile").click()
        time.sleep(0.5)

        # 여러 프로필 중 선택
        post_blog_account = browser.find_elements(By.CSS_SELECTOR, ".img_common_tistory.link_edit")
        post_blog_account[self.tstory_num - 1].click()
        time.sleep(1)

        # 이전 작업이 있을 경우 취소
        try:
            result = browser.switch_to.alert
            result.dismiss()
        except:
            pass

        browser.switch_to.frame("editor-tistory_ifr")

        # 메모장 원고 가져오기
        file = open(post_save_path, 'r', encoding='UTF-8')
        contents = file.readlines()
        file.close()

        for content in contents[2:]:
            browser.find_element(By.CSS_SELECTOR, "#tinymce").send_keys(content)

        time.sleep(1)

        browser.switch_to.default_content()

        browser.find_element(By.CSS_SELECTOR, ".action").click()
        time.sleep(1)

        browser.quit()

        self.update_status.emit(f"\n포스팅 {post_cnt}개 임시저장 완료!\n")












    def naver_post(self, post_cnt, post_save_path):

        chrome_options2 = Options()
        chrome_options2.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options2.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(executable_path=ChromeDriverManager().install())


        # 포스팅 작업
        browser = webdriver.Chrome(service=service, options=chrome_options2)

        url = "https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/"

        # 웹페이지 해당 주소 이동
        browser.implicitly_wait(5)
        browser.maximize_window()
        browser.get(url)


        time.sleep(3)

        # 아이디 입력
        id = browser.find_element(By.CSS_SELECTOR, "#id")
        id.click()
        pyperclip.copy(self.ID)
        pyautogui.hotkey("ctrl", "v")


        # 비밀번호 입력
        pw = browser.find_element(By.CSS_SELECTOR, "#pw")
        pw.click()
        pyperclip.copy(self.PW)
        pyautogui.hotkey("ctrl", "v")


        # 로그인 버튼
        login_btn = browser.find_element(By.CSS_SELECTOR, "#log\.login")
        login_btn.click()

        # 로그인 브라우저 등록
        try:
            browser.find_element(By.CSS_SELECTOR, "#new\.save").click()
        except:
            pass

        # 변경사항
        browser.get(f"https://blog.naver.com/{self.ID}?Redirect=Write")
        time.sleep(3)

        browser.switch_to.frame("mainFrame")

        # 작성중인 글이 있는 경우
        try:
            browser.find_element(By.CSS_SELECTOR, ".se-popup-button.se-popup-button-cancel").click()

        except:
            pass
        
        file = open(post_save_path, 'r', encoding='UTF-8')
        contents = file.readlines()
        file.close()

        browser.find_element(By.XPATH, "//span[contains(text(), '본문에 #을')]").click()  # 웹 요소 찾기
        time.sleep(1)
        action = ActionChains(browser)  # 액션 지정
        time.sleep(1)
        for content in contents[2:]:
            action.send_keys(content).perform()

        time.sleep(1.5)

        # 에디터 도움말 화면이 뜬 경우
        try:
            browser.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button").click()
            time.sleep(1)

        except:
            pass

        browser.find_element(By.CSS_SELECTOR, ".save_btn___RzjY").click()

        browser.quit()

        self.update_status.emit(f"\n포스팅 {post_cnt}개 임시저장 완료!\n")










    def kakao_post(self, post_cnt, post_save_path):

        chrome_options2 = Options()
        chrome_options2.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options2.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(executable_path=ChromeDriverManager().install())

        # 포스팅 작업
        browser = webdriver.Chrome(service=service, options=chrome_options2)

        url = "https://www.tistory.com/auth/login"

        # 웹페이지 해당 주소 이동
        browser.implicitly_wait(5)
        browser.maximize_window()
        browser.get(url)

        time.sleep(3)

        # 카카오 계정으로 로그인 클릭
        browser.find_element(By.CSS_SELECTOR, ".btn_login.link_kakao_id").click()
        time.sleep(2)

        # 아이디, 비밀번호 입력
        browser.find_element(By.CSS_SELECTOR, "#loginId--1").send_keys(self.ID)
        browser.find_element(By.CSS_SELECTOR, "#password--2").send_keys(self.PW)
        time.sleep(1)

        # 로그인 클릭
        browser.find_element(By.CSS_SELECTOR, ".btn_g.highlight.submit").click()
        time.sleep(1.5)

        # 프로필 클릭
        browser.find_element(By.CSS_SELECTOR, ".link_profile").click()
        time.sleep(0.5)

        # 여러 프로필 중 선택
        post_blog_account = browser.find_elements(By.CSS_SELECTOR, ".img_common_tistory.link_edit")
        post_blog_account[self.tstory_num - 1].click()
        time.sleep(1)

        # 이전 작업이 있을 경우 취소
        try:
            result = browser.switch_to.alert
            result.dismiss()
        except:
            pass

        browser.switch_to.frame("editor-tistory_ifr")

        # 메모장 원고 가져오기
        file = open(post_save_path, 'r', encoding='UTF-8')
        contents = file.readlines()
        file.close()

        for content in contents[2:]:
            browser.find_element(By.CSS_SELECTOR, "#tinymce").send_keys(content)

        time.sleep(1)

        browser.switch_to.default_content()

        browser.find_element(By.CSS_SELECTOR, ".action").click()
        time.sleep(1)

        browser.quit()

        self.update_status.emit(f"\n포스팅 {post_cnt}개 임시저장 완료!\n")





    def naver_post(self, post_cnt, post_save_path):

        chrome_options2 = Options()
        chrome_options2.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options2.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(executable_path=ChromeDriverManager().install())

        # 포스팅 작업
        browser = webdriver.Chrome(service=service, options=chrome_options2)

        url = "https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/"

        # 웹페이지 해당 주소 이동
        browser.implicitly_wait(5)
        browser.maximize_window()
        browser.get(url)


        time.sleep(3)

        # 아이디 입력
        id = browser.find_element(By.CSS_SELECTOR, "#id")
        id.click()
        pyperclip.copy(self.ID)
        pyautogui.hotkey("ctrl", "v")


        # 비밀번호 입력
        pw = browser.find_element(By.CSS_SELECTOR, "#pw")
        pw.click()
        pyperclip.copy(self.PW)
        pyautogui.hotkey("ctrl", "v")


        # 로그인 버튼
        login_btn = browser.find_element(By.CSS_SELECTOR, "#log\.login")
        login_btn.click()

        # 로그인 브라우저 등록
        try:
            browser.find_element(By.CSS_SELECTOR, "#new\.save").click()
        except:
            pass

        # 변경사항
        browser.get(f"https://blog.naver.com/{self.ID}?Redirect=Write")
        time.sleep(3)

        browser.switch_to.frame("mainFrame")

        # 작성중인 글이 있는 경우
        try:
            browser.find_element(By.CSS_SELECTOR, ".se-popup-button.se-popup-button-cancel").click()

        except:
            pass

        file = open(post_save_path, 'r', encoding='UTF-8')
        contents = file.readlines()
        file.close()

        browser.find_element(By.XPATH, "//span[contains(text(), '본문에 #을')]").click()  # 웹 요소 찾기
        time.sleep(1)
        action = ActionChains(browser)  # 액션 지정
        time.sleep(1)
        for content in contents[2:]:
            action.send_keys(content).perform()

        time.sleep(1.5)

        # 에디터 도움말 화면이 뜬 경우
        try:
            browser.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button").click()
            time.sleep(1)

        except:
            pass

        browser.find_element(By.CSS_SELECTOR, ".save_btn___RzjY").click()

        browser.quit()

        self.update_status.emit(f"\n포스팅 {post_cnt}개 임시저장 완료!\n")





class Maindialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(os.path.join(BASE_DIR, UI_PATH), self)

        self.url_dirName = ""
        self.link_dirName = ""

        # 그룹 1 생성 및 'naver' 라디오 버튼 추가
        self.group1 = QtWidgets.QButtonGroup(self)
        self.group2 = QtWidgets.QButtonGroup(self)
        self.group3 = QtWidgets.QButtonGroup(self)
        
        self.group1.addButton(self.gpt_free)
        self.group1.addButton(self.gpt_16k)
        self.group1.addButton(self.gpt_4)

        self.group2.addButton(self.naver)  # 'naver'는 Qt Designer에서 라디오 버튼에 설정한 objectName
        self.group2.addButton(self.tstory)

        self.group3.addButton(self.tstory_account)
        self.group3.addButton(self.kakao_account)


        # 1) 버튼 클릭 이벤트
        # self.객체이름.clicked.connect(self.실행함수이름)
        self.check_keyword.clicked.connect(self.keyword_click)
        self.check_blog_url.clicked.connect(self.blog_url_click)
        self.check_blog_link.clicked.connect(self.blog_link_click)


        self.blog_url.clicked.connect(self.url_click)
        self.blog_link.clicked.connect(self.link_click)

        self.tstory.clicked.connect(self.tstory_click)
        self.naver.clicked.connect(self.naver_click)

        # 실행, 중지, 리셋, 종료 버튼 클릭
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.reset_btn.clicked.connect(self.reset)
        self.close_btn.clicked.connect(self.exit)
        
        # 초기에 버튼을 숨김
        self.keyword.setVisible(False)
        self.blog_url.setVisible(False)
        self.blog_link.setVisible(False)
        self.generate_post.setVisible(False)
        self.label_7.setVisible(False)
        self.tstory_account.setVisible(False)
        self.kakao_account.setVisible(False)
        self.line_9.setVisible(False)
        self.tstory_num.setVisible(False)

        settings = QSettings("애드센스", "이성현")
        self.key.setText(settings.value("key", ""))

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
            
        if self.naver.isChecked() == False and self.tstory.isChecked() == False:
            pyautogui.alert("포스팅할 블로그를 설정하세요.")
            return
        elif self.tstory.isChecked():
            if self.tstory_account.isChecked() == False and self.kakao_account.isChecked() == False:
                pyautogui.alert("포스팅할 블로그를 설정하세요.")
                return
            
        # id, pw 체크
        if self.ID.text() == "" or self.PW.text() == "":
            pyautogui.alert("아이디 또는 비밀번호를 입력하세요.")
            return
                    
        
        input_ID = self.ID.text()
        input_PW = self.PW.text()

        # 글자수, 진행 상황 초기화
        self.textBrowser.setText("")
        self.status.setText("")

        api_key = self.key.text()

        post_blog = 0

        # 포스팅할 블로그 체크
        if self.naver.isChecked():
            post_blog = 1

        elif self.tstory.isChecked():
            if self.tstory_account.isChecked():
                post_blog = 2
            else:
                post_blog = 3


        settings = QSettings("애드센스", "이성현")
        settings.setValue("key", api_key)

        # 저장 경로 설정
        save_path = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)

        if save_path == "":
            pyautogui.alert("저장 경로를 설정해주세요.")
            return

        input_generate_post = self.generate_post.value()
        input_tstory_num = self.tstory_num.value()

        ver = self.select_ver()

        self.status.append("실행중....")

        # 체크박스 키워드가 선택되었을 경우
        if self.check_keyword.isChecked():
            input_keyword = self.keyword.text()

            self.second_thread = secondThread(ver, input_keyword, None, None, save_path, input_generate_post, api_key, post_blog, input_ID, input_PW, input_tstory_num)
            self.second_thread.check_keyword = 1
            self.second_thread.update_status.connect(self.update_status)
            self.second_thread.update_textbrowser.connect(self.update_textbrowser)
    
            self.second_thread.start()

        # 체크박스 블로그 주소로 선택되었을 경우
        elif self.check_blog_url.isChecked():

            self.second_thread = secondThread(ver, None, self.url_dirName, None, save_path, input_generate_post, api_key, post_blog, input_ID, input_PW, input_tstory_num)
            self.second_thread.check_url = 1
            self.second_thread.update_status.connect(self.update_status)
            self.second_thread.update_textbrowser.connect(self.update_textbrowser)

            self.second_thread.start()

        
        # 체크박스 블로그 링크로 선택되었을 경우
        elif self.check_blog_link.isChecked():

            self.second_thread = secondThread(ver, None, None, self.link_dirName, save_path, None, api_key, post_blog, input_ID, input_PW, input_tstory_num)
            self.second_thread.check_link = 1

            self.second_thread.update_status.connect(self.update_status)
            self.second_thread.update_textbrowser.connect(self.update_textbrowser)
    
            self.second_thread.start()


    def stop(self):
        self.second_thread.terminate()
        self.status.append("\n프로그램 중지\n")

    def update_status(self, string):
        self.status.append(f"{string}")

    def update_textbrowser(self, string):
        self.textBrowser.append(f"{string}")

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

    def tstory_click(self):
        if self.tstory.isChecked():
            self.tstory_account.setVisible(True)
            self.kakao_account.setVisible(True)
            self.line_9.setVisible(True)
            self.tstory_num.setVisible(True)    
        else:
            self.tstory_account.setVisible(False)
            self.kakao_account.setVisible(False)            
    
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

    def naver_click(self):
        if self.tstory_account.isVisible():
            self.tstory_account.setVisible(False)
            self.kakao_account.setVisible(False)
            self.line_9.setVisible(False)
            self.tstory_num.setVisible(False)


    def exit(self):
        sys.exit()


QApplication.setStyle("fusion")
app = QApplication(sys.argv)
main_dialog = Maindialog()
main_dialog.show()

sys.exit(app.exec_())
