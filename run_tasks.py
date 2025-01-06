import schedule
import time
import django
import os
import sys
from app1 import tasks

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proiect.settings')
django.setup()

def run_scheduler():
    schedule.every(2).minutes.do(tasks.delete_users)
    schedule.every().monday.at("08:00").do(tasks.send_newsletter)
    schedule.every(20).seconds.do(tasks.create_film_schedule)
    schedule.every(30).minutes.do(tasks.remind_admins)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("Scheduler oprit manual.")
        sys.exit()
   

