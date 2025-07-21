from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


from auth.routes import router as auth_router
from items.routes import app as items_router
from websocket.routes import app as websocket_router
from jobs.scheduler import start_scheduler, shutdown_scheduler
from userprofile.routes import app as profile_router


app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(items_router, prefix="/items", tags=["Items"])
app.include_router(websocket_router, prefix="/ws/bid", tags=["WebSocket"])
app.include_router(profile_router, prefix="/profile", tags=["Profile"])

# APScheduler setup

@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
   shutdown_scheduler()

@app.get("/")
def root():
   return {"message": "Scheduler running"}