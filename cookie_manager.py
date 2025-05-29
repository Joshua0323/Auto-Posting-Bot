# cookie_manager.py
import pickle
from pathlib import Path
import time

def load_cookies(driver, path="cookies.pkl", url="https://daum.net"):
    """쿠키를 파일에서 불러와 브라우저에 적용"""
    if not Path(path).exists():
        return False
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        driver.get(url)
        for cookie in cookies:
            if "sameSite" in cookie:
                del cookie["sameSite"]
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ 쿠키 추가 실패: {e}")
    return True

def save_cookies(driver, path="cookies.pkl"):
    """브라우저의 현재 쿠키를 파일로 저장"""
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)