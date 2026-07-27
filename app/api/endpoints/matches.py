import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy import func

from app.db.session import SessionsLocal
from app.db.models import Match, OddsHistory
# --- IMPORT YOUR SETTINGS HERE ---
# (Adjust this path if your Settings class is in a different file, like app.core.config)
from app.core.config import settings  

router = APIRouter()

# Use your type-safe settings instead of raw os.getenv!
ODDS_API_KEY = settings.ODDS_API_KEY
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"

def get_db():
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_matches(db: Session = Depends(get_db)):
    """
    Get all tracked matches along with their metadata.
    """
    matches = db.query(Match).all()
    return matches


@router.get("/{match_id}/history")
def get_match_odds_history(match_id: str, db: Session = Depends(get_db)):
    """
    Get the chronological historical odds timeline for a specific match.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    history = (
        db.query(OddsHistory)
        .filter(OddsHistory.match_id == match_id)
        .order_by(OddsHistory.fetched_at.asc())
        .all()
    )

    return {
        "match": {
            "id": match.id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "commence_time": match.commence_time
        },
        "history": [
            {
                "id": record.id,
                "sportsbook": record.sportsbook,
                "team_name": record.team_name,
                "price": record.price,
                "fetched_at": record.fetched_at
            }
            for record in history
        ],
        "history_count": len(history)
    }


# --- 🏈 LIVE DATA SYNC ENDPOINT ---
# --- 🏈 LIVE DATA SYNC ENDPOINT ---
@router.post("/fetch-live")
def fetch_live_odds(db: Session = Depends(get_db)):
    """
    Hits The Odds API, synchronizes the match metadata, and logs 
    new price updates into OddsHistory if they differ from the latest entry.
    """
    if not ODDS_API_KEY:
        raise HTTPException(status_code=500, detail="ODDS_API_KEY missing.")

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
        "dateFormat": "iso"
    }

    try:
        response = requests.get(ODDS_API_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Odds API Error: {response.text}")
        api_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")

    sync_time = datetime.now(timezone.utc)
    updated_matches_count = 0
    new_price_records_count = 0

    try:
        for event in api_data:
            match_id = event["id"]
            commence_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))

            # 1. Upsert Match
            match_record = db.query(Match).filter(Match.id == match_id).first()
            if not match_record:
                match_record = Match(
                    id=match_id,
                    sport_key=event.get("sport_key", "americanfootball_nfl"),
                    home_team=event["home_team"],
                    away_team=event["away_team"],
                    commence_time=commence_time
                )
                db.add(match_record)
            else:
                match_record.commence_time = commence_time
            
            updated_matches_count += 1
            db.flush()

            # 2. Extract Odds safely
            for bookmaker in event.get("bookmakers", []):
                bookmaker_name = bookmaker["title"]
                
                for market in bookmaker.get("markets", []):
                    if market["key"] != "h2h":
                        continue
                    
                    for outcome in market.get("outcomes", []):
                        team_name = outcome["name"]
                        
                        # SAFE PARSING: Handle missing or weird price formats
                        raw_price = outcome.get("price")
                        if raw_price is None:
                            continue # Bookie pulled the line off the board
                        
                        try:
                            # Safely convert to int (handles if API sends 150.0)
                            current_price = int(float(raw_price))
                        except (ValueError, TypeError):
                            continue # Skip unparseable odds

                        # Deduplication Check
                        last_record = (
                            db.query(OddsHistory)
                            .filter(
                                OddsHistory.match_id == match_id,
                                OddsHistory.sportsbook == bookmaker_name,
                                OddsHistory.team_name == team_name
                            )
                            .order_by(OddsHistory.fetched_at.desc())
                            .first()
                        )

                        # ALWAYS INSERT if database is completely empty (last_record is None)
                        # Or if the price has moved.
                        if last_record is None or last_record.price != current_price:
                            new_history = OddsHistory(
                                match_id=match_id,
                                sportsbook=bookmaker_name,
                                team_name=team_name,
                                price=current_price,
                                fetched_at=sync_time
                            )
                            db.add(new_history)
                            new_price_records_count += 1

        db.commit()
        return {
            "status": "success",
            "matches_synchronized": updated_matches_count,
            "new_price_movements_logged": new_price_records_count,
            "message": "Data saved successfully!"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
@router.post("/clear-all-history")
def clear_history(db: Session = Depends(get_db)):
    # Delete the child history records first to satisfy foreign key constraints
    db.query(OddsHistory).delete()
    # Delete the old matches too!
    db.query(Match).delete()
    db.commit()
    return {"message": "Database completely wiped! Now scan live odds for a 100% clean slate."}

@router.get("/debug-db")
def debug_database(db: Session = Depends(get_db)):
    """
    Diagnostic endpoint to inspect database rows and relations.
    """
    total_matches = db.query(Match).count()
    total_history = db.query(OddsHistory).count()
    
    # Get a sample match
    sample_match = db.query(Match).first()
    sample_match_data = None
    if sample_match:
        sample_match_data = {
            "id": sample_match.id,
            "home_team": sample_match.home_team,
            "away_team": sample_match.away_team
        }
        
    # Get a sample history record
    sample_history = db.query(OddsHistory).first()
    sample_history_data = None
    if sample_history:
        sample_history_data = {
            "id": sample_history.id,
            "match_id": sample_history.match_id,
            "sportsbook": sample_history.sportsbook,
            "price": sample_history.price
        }

    return {
        "database_stats": {
            "total_matches_in_db": total_matches,
            "total_history_rows_in_db": total_history,
        },
        "sample_match_record": sample_match_data,
        "sample_history_record": sample_history_data,
        "are_they_linking": "No history records found to link!" if total_history == 0 else (
            "Yes, matching IDs exist!" if sample_history and sample_match and sample_history.match_id == sample_match.id else "No, match_ids do not line up!"
        )
    }
def american_to_implied_prob(american_odds: int) -> float:
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return -american_odds / (-american_odds + 100)

@router.get("/arbitrage")

def find_arbitrage_opportunities(db: Session = Depends(get_db)):
    """
    Queries the database, finds the maximum moneyline odds across sportsbooks for home/away teams, 
    and checks if an arbitrage opportunity exists.
    """
    try:
        matches = db.query(Match).all()
        arbitrage_opportunities = []

        for match in matches:
            # 1. Grab all history for this match sorted newest to oldest
            history = (
                db.query(OddsHistory)
                .filter(OddsHistory.match_id == match.id)
                .order_by(OddsHistory.fetched_at.desc())
                .all()
            )

            if not history:
                continue

            # 2. Get the latest timestamp logged for this match
            latest_timestamp = history[0].fetched_at

            # 3. Filter history in Python for records within 2 seconds of the latest fetch 
            # (Prevents SQL microsecond mismatch errors while ignoring stale old fetches)
            latest_odds = [
                record for record in history 
                if abs((record.fetched_at - latest_timestamp).total_seconds()) < 2
            ]

            best_odds = {
                "home": {"price": -999999, "sportsbook": None},
                "away": {"price": -999999, "sportsbook": None}
            }

            for record in latest_odds:
                if record.team_name == match.home_team:
                    if record.price > best_odds["home"]["price"]:
                        best_odds["home"]["price"] = record.price
                        best_odds["home"]["sportsbook"] = record.sportsbook
                elif record.team_name == match.away_team:
                    if record.price > best_odds["away"]["price"]:
                        best_odds["away"]["price"] = record.price
                        best_odds["away"]["sportsbook"] = record.sportsbook

            # Skip if we don't have valid odds for both sides of the matchup
            if best_odds["home"]["price"] == -999999 or best_odds["away"]["price"] == -999999:
                continue

            prob_home = american_to_implied_prob(best_odds["home"]["price"])
            prob_away = american_to_implied_prob(best_odds["away"]["price"])
            total_implied_prob = prob_home + prob_away

            if total_implied_prob < 1.0:
                roi = ((1.0 / total_implied_prob) - 1.0) * 100.0

                formatted_arb = {
                    "id": f"arb-{match.id}",
                    "matchup": f"{match.away_team} @ {match.home_team}",
                    "sport": "NFL Football",
                    "profitMargin": round(roi, 2),
                    "outcomes": [
                        {
                            "team": match.away_team,
                            "sportsbook": best_odds["away"]["sportsbook"],
                            "americanOdds": f"+{best_odds['away']['price']}" if best_odds["away"]["price"] > 0 else str(best_odds["away"]["price"]),
                            "impliedProb": prob_away
                        },
                        {
                            "team": match.home_team,
                            "sportsbook": best_odds["home"]["sportsbook"],
                            "americanOdds": f"+{best_odds['home']['price']}" if best_odds["home"]["price"] > 0 else str(best_odds["home"]["price"]),
                            "impliedProb": prob_home
                        }
                    ]
                }
                arbitrage_opportunities.append(formatted_arb)

        return arbitrage_opportunities

    except Exception as e:
        print(f"Error executing /arbitrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Arbitrage error: {str(e)}")