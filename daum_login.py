import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
from dotenv import load_dotenv

def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("post_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# ✅ .env 로드
load_dotenv()

# ✅ 사용자 정보 (보안 처리된 방식)
user_id = os.getenv("DAUM_ID")
user_pw = os.getenv("DAUM_PW")

if not user_id or not user_pw:
    print("❌ .env 파일에 DAUM_ID 또는 DAUM_PW 값이 없습니다.")
    exit()

# ✅ 글쓰기 정보 불러오기 (.json)
with open("post_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    post_title = data["title"]
    post_content = data["content"]

# ✅ 드라이버 실행
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# ✅ 로그인 처리
print("🔐 로그인 진행 중...")
driver.get("https://logins.daum.net/accounts/loginform.do")
wait.until(EC.presence_of_element_located((By.ID, "loginId--1"))).send_keys(user_id)
wait.until(EC.presence_of_element_located((By.ID, "password--2"))).send_keys(user_pw)
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn_g.highlight"))).click()
wait.until(EC.url_contains("daum.net"))
print("✅ 로그인 성공")

# ✅ 게시판 접속 및 iframe 준비
driver.get("https://cafe.daum.net/skc67/8eaR")
time.sleep(3)
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"✅ 현재 페이지의 iframe 수: {len(iframes)}")
for iframe in iframes:
    if "down" in iframe.get_attribute("id"):
        driver.switch_to.frame(iframe)
        print("✅ iframe#down 전환 성공")
        break
else:
    print("⚠️ iframe#down 없음 – 전환 생략")

# ✅ 게시판 재접속 및 iframe 진입
driver.get("https://cafe.daum.net/skc67/8eaR")
time.sleep(2)
wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#down")))
print("✅ 게시판 iframe 진입 완료")

# ✅ 기존 게시글 중복 여부 확인 (2번 스크롤 + 제목 검색)
print("🔍 기존 게시글 제목 탐색 중...")

post_exists = False
title_to_check = post_title.strip()

scroll_container = driver.find_element(By.TAG_NAME, 'body')

for i in range(2):  # 스크롤 2번
    scroll_container.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    titles = driver.find_elements(By.CSS_SELECTOR, "a.txt_item")  # ← 수정된 선택자
    for t in titles:
        text = t.text.strip()
        print(f" - 확인된 제목: {text}")
        if title_to_check == text:
            print(f"✅ 중복 글 발견: {text}")
            post_exists = True
            break

    if post_exists:
        break

if post_exists:
    print("🚫 중복 글이 발견되어 글쓰기를 건너뜁니다.")
    write_log(f"중복 글로 등록 생략: {post_title}")
    driver.quit()
    exit()
else:
    print("🆗 동일한 제목의 기존 글 없음. 글쓰기를 계속 진행합니다.")


# ✅ 글쓰기 버튼 클릭
try:
    write_button = wait.until(EC.element_to_be_clickable((By.ID, "article-write-btn")))
    write_button.click()
    print("✅ 글쓰기 버튼 클릭 완료")
    time.sleep(4)
except Exception as e:
    print("❌ 글쓰기 버튼 클릭 실패:", e)
    write_log(f"❌ 글쓰기 버튼 클릭 실패 – 오류: {str(e)}")
    driver.quit()
    exit()

# ✅ 글쓰기 에디터 iframe 탐색
driver.switch_to.default_content()
time.sleep(1)
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"✅ 글쓰기 창 iframe 수: {len(iframes)}")
editor_iframe = None
for index, iframe in enumerate(iframes):
    print(f"🔍 iframe {index} - id: {iframe.get_attribute('id')} | class: {iframe.get_attribute('class')}")
    driver.switch_to.default_content()
    try:
        driver.switch_to.frame(iframe)
        title_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='제목을 입력하세요.']"))
        )
        editor_iframe = iframe
        print(f"✅ 에디터 iframe 전환 성공 (index={index})")
        break
    except:
        continue

if not editor_iframe:
    print("❌ 에디터 iframe 탐색 실패")
    write_log("❌ 에디터 iframe 탐색 실패 – 글쓰기 중단됨")
    driver.save_screenshot("missing_editor_iframe.png")
    driver.quit()
    exit()

# ✅ 제목 입력 (JS + 이벤트 트리거)
try:
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, title_input, post_title)
    print("✅ 제목 입력 완료")
except Exception as e:
    print("❌ 제목 입력 실패:", e)
    driver.save_screenshot("title_input_fail.png")
    driver.quit()
    exit()

# ✅ 본문 입력 및 등록
try:
    editor_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#keditorContainer_ifr")))
    driver.switch_to.frame(editor_iframe)
    editor_body = wait.until(EC.presence_of_element_located((By.ID, "tinymce")))
    driver.execute_script("""
        arguments[0].innerHTML = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, editor_body, post_content.replace("\n", "<br>"))
    print("✅ 본문 입력 완료")

    # ✅ 등록 버튼 클릭
    driver.switch_to.default_content()
    driver.switch_to.frame(iframes[0])  # 에디터 iframe으로 재전환
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '등록')]")))
    submit_btn.click()
    print("✅ 게시글 등록 완료")
    write_log(f"게시글 등록 완료: {post_title}")

except Exception as e:
    print("❌ 등록 실패:", e)
    write_log(f"❌ 게시글 등록 실패: {post_title} | 오류: {str(e)}")
    driver.save_screenshot("submit_fail.png")

# ✅ 종료 전 대기 후 드라이버 종료
time.sleep(2)
driver.quit()
