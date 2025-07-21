from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from jobs.auction_service import finalize_ended_auctions

# Required if event loop is already running (e.g., FastAPI)


scheduler = BackgroundScheduler()

main_loop = asyncio.get_event_loop()  # Get it once during startup

def run_finalize_job():
    print("[JOB TRIGGERED] Scheduling async task on main loop...")
    try:
        asyncio.run_coroutine_threadsafe(finalize_ended_auctions(), main_loop)
        print("[JOB TRIGGERED] Task scheduled successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to schedule async job: {e}")



def start_scheduler():
    global main_loop
    main_loop = asyncio.get_event_loop()
    
    print("Starting scheduler...")
    scheduler.add_job(
        run_finalize_job,
        trigger=IntervalTrigger(seconds=10),
        id="finalize_auctions",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started!")

def shutdown_scheduler():
    scheduler.shutdown(wait=False)
