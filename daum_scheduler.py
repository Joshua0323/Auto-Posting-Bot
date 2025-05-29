# daum_scheduler.py
import schedule
import time
from daum_post_bot import run_bot

schedule.every(30).seconds.do(run_bot)

print("📅 Daum 자동 게시 스케줄 시작됨. 대기 중...")

while True:
    schedule.run_pending()
    time.sleep(30)