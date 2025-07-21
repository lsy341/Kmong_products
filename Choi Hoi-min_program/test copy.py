import re

def remove_special_characters(input_string):
    # 특수 문자 패턴 정의
    special_chars_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/]')

    # 입력 문자열에서 특수 문자를 삭제
    clean_string = re.sub(special_chars_pattern, '', input_string)

    return clean_string

# 입력 문자열
input_string = "안녕하세요 이것은 예제 문자열입니다."

# 특수 문자 삭제 함수 호출
cleaned_string = remove_special_characters(input_string)

# 결과 출력
print("원본 문자열:", input_string)
print("특수 문자 제거된 문자열:", cleaned_string)
