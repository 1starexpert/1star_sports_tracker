from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import matches
from app.db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Betting Arbitrage & Analytics API")

# 2. Configure allowed origins (Include Vercel + Localhost)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.vercel.app",  # Allows Vercel deployments
    "*"                      # Allow all for testing
]

# 3. Add the middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Set to ["*"] to grant access globally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])

@app.get("/")
def root():
    return {"message": "Sports Tracker API is running smoothly"}
