from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ✅ 사용자 정보
user_id = "ijhsj1229@gmail.com"         # ← 본인 ID 입력
user_pw = "DLAwlgh0323."   # ← 본인 PW 입력

# ✅ 글쓰기 정보
post_title = "💻 느려진 컴퓨터🐢, 소음🤬 및 집 와이파이 문제! 빠르게 해결해드려요❗❗"
post_content = "이 글은 Selenium 자동화 테스트입니다.\n내용 예시입니다."

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

# ✅ 페이지 스크롤 다운
body = driver.find_element(By.TAG_NAME, 'body')
body.click()
for i in range(2):
    body.send_keys(Keys.PAGE_DOWN)
    print(f"[DEBUG] PAGE_DOWN {i+1}")
    time.sleep(0.5)

# ✅ 글쓰기 버튼 클릭
try:
    write_button = wait.until(EC.element_to_be_clickable((By.ID, "article-write-btn")))
    write_button.click()
    print("✅ 글쓰기 버튼 클릭 완료")
    time.sleep(4)
except Exception as e:
    print("❌ 글쓰기 버튼 클릭 실패:", e)
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
    driver.save_screenshot("missing_editor_iframe.png")
    driver.quit()
    exit()

# ✅ 제목 입력
try:
    title_input.send_keys(post_title)
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
    body = wait.until(EC.presence_of_element_located((By.ID, "tinymce")))
    body.click()
    body.send_keys(post_content)
    print("✅ 본문 입력 완료")

    # ✅ 등록 버튼 클릭
    driver.switch_to.default_content()
    driver.switch_to.frame(iframes[0])  # 에디터 iframe으로 재전환
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '등록')]")))
    submit_btn.click()
    print("✅ 게시글 등록 완료")

except Exception as e:
    print("❌ 등록 실패:", e)
    driver.save_screenshot("submit_fail.png")

# ✅ 종료 전 대기 후 드라이버 종료
time.sleep(2)
driver.quit()


