from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import matches
from app.db.session import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Betting Arbitrage & Analytics API")

# Add your EXACT Vercel domain here (no trailing slash)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://1star-sports-tracker-6v1yyq20s-nyxmere.vercel.app/",  # <--- REPLACE THIS WITH YOUR ACTUAL VERCEL URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Pass the list directly (NO WILDCARDS with credentials)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])

@app.get("/")
def root():
    return {"message": "Sports Tracker API is running smoothly"}