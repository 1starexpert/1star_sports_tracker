from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. Import the middleware
from app.api.endpoints import matches
from app.db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Betting Arbitrage & Analytics API")

# 2. Configure the allowed origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 3. Add the middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])

@app.get("/")
def root():
    return {"message": "Sports Tracker API is running smoothly"}


"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import matches
from app.db.database import engine, Base
# from app.services.fetcher import fetch_live_mlb_odds

app = FastAPI(title="Sports Analytics Dashboard API")

@app.get("/")
def root():
    return {"status": "healthy", "message": "Pipeline backend is online"}

app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])


"""


