from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롬 드라이버 초기화
driver = webdriver.Chrome()

# 웹 페이지 열기
driver.get("https://example.com")

try:
    # 웹 드라이버가 최대 5초간 Alert를 기다림
    WebDriverWait(driver, 5).until(EC.alert_is_present())

    # Alert 창에 접근
    alert = driver.switch_to.alert
    print(f"Alert detected: {alert.text}")

    # 필요한 경우, 여기서 Alert 창을 닫거나 다른 조치를 취할 수 있습니다.
    alert.accept()  # 또는 alert.dismiss()

except (TimeoutException, NoAlertPresentException):
    # Alert가 나타나지 않았거나, 이미 사라졌을 경우
    print("No alert present.")

except UnexpectedAlertPresentException as e:
    # 다른 예상치 못한 Alert가 나타났을 경우
    print(f"Unexpected alert present: {str(e)}")