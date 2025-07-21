from time import sleep
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def example_job():
    print(f"Example job executed at {datetime.now()}")
    # Simulate some work
    print("Example job completed")

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(example_job, 'interval', seconds=5)
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
