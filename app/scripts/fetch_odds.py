import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionsLocal

# Import spreadsheet models here:

from app.db.models import Match, OddsHistory

def fetch_live_odds():
    """
    Hits the Odds API to fetch upcoming sports matches and their betting lines.
    """
    # Using 'americanfootball_nfl' as an example since it uses American moneyline prices (-100, 150)

    SPORT = "americanfootball_nfl"
    REGIONS = "us"
    MARKETS = "h2h"

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

    params = {
        "apiKey": settings.ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american" # Changed to american to match Integer price format...

    }
    print(f"📡 Fetching live data from The Odds API for {SPORT}...")
    response = requests.get(url, params=params)

    if response.status_code != 200: 
        print(f"❌ Failed to fetch data: {response.status_code} - {response.text}")
        return None
    
    data = response.json()
    print(f"✅ Successfully fetched {len(data)} matches!")
    return data

def save_to_database(db: Session, api_data: list):
    """
    Parses the JSON data and saves / updates records in PostgreSQL
    """
    if not api_data:
        print("⚠️ No data received to save.")
        return
    
    print(f"🗄️ Starting database sync for {len(api_data)} games...")
    fetched_at_time = datetime.utcnow()
    odds_logged_counter = 0

    for game in api_data:
        game_id = game["id"]
        sport_key = game["sport_key"]
        home_team = game["home_team"]
        away_team = game["away_team"]
        commence_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))

        # Upsert match profile
        match_record = db.query(Match).filter(Match.id == game_id).first()
        if not match_record:
            match_record = Match(
                id=game_id,
                sport_key=sport_key,
                home_team=home_team,
                away_team=away_team,
                commence_time=commence_time
            )
            db.add(match_record)
        else:
            match_record.commence_time = commence_time

        # Process bookmakers
        if "bookmakers" in game and game["bookmakers"]:
            for bookie in game["bookmakers"]:
                sportsbook_name = bookie["title"]
                
                for market in bookie["markets"]:
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            team_name = outcome["name"]
                            price = int(outcome["price"])
                            
                            odds_entry = OddsHistory(
                                match_id=game_id,
                                sportsbook=sportsbook_name,
                                team_name=team_name,
                                price=price,
                                fetched_at=fetched_at_time
                            )
                            db.add(odds_entry)
                            odds_logged_counter += 1

    # Force SQLAlchemy to write all accumulated records to Postgres
    print(f"💾 Staging complete. Total odds rows prepared: {odds_logged_counter}")
    print("⏳ Committing transaction to database...")
    db.commit()
    print("🏁 Database sync complete!")

    """
    if not api_data:
        print("⚠️ No data received to save.")
        return
    
    # --- TEMPORARY DIAGNOSTIC PRINT ---
    print("\n🔍 DEBUGGING FIRST GAME PAYLOAD:")
    import json
    print(json.dumps(api_data[0], indent=2))
    print("="*40 + "\n")
    # ----------------------------------

    print(f"🗄️ Processing and saving records to Postgres...")
    # ... rest of your code stays exactly the same ...

    print("🗄️ Processing and saving records to Postgres...")
    fetched_at_time = datetime.utcnow() # gives our scrape one consistent time stamp

    for game in api_data:
        # extract the base match profile:
        game_id = game["id"]
        sport_key = game["sport_key"]
        home_team = game["home_team"]
        away_team = game["away_team"]

        # 1. Convert the time stamp from the API into date time object of Python
        commence_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))

        # 2. Check if this match already exists in our spreadsheet (Upsert) 
        match_record = db.query(Match).filter(Match.id == game_id).first()

        if not match_record:
            # If no matching record found, then it is a brand new game. A new match profile object is needed.
            print(f"✨ New match found: {home_team} vs {away_team}")
            match_record = Match(
                id=game_id,
                sport_key = sport_key,
                home_team=home_team,
                away_team=away_team,
                commence_time=commence_time
            )
            db.add(match_record)
        else:
            # Else matching record found. Just update the start time if it changed.
            match_record.commence_time = commence_time
        
        # 3. Dig inside the bookmark array to log prices...
        if "bookmarkers" in game and game["bookmarkers"]:
            for bookie in game["bookmarkers"]:
                sportsbook_name = bookie["title"] # e.g. Draft Kings

                for market in bookie["markets"]:
                    if market["key"] == "h2h": # ensure that it is a head to head moneyline
                        for outcome in market["outcomes"]:
                            team_name = outcome["name"]  # e.g. Toronto Blue Jays
                            price = int(outcome["price"]) # e.g. -130

                            # Create a brand new historical row log object (In Spreadsheet 2):
                            odds_entry = OddsHistory(
                                match_id=game_id,
                                sportsbook=sportsbook_name,
                                team_name=team_name,
                                price=price,
                                fetched_at=fetched_at_time
                            )
                            db.add(odds_entry)
"""


    #Commit all changes to the database:
    db.commit()

    print("🏁 Database sync complete!")

if __name__ == "__main__":
    db = SessionsLocal()
    try:
        raw_data = fetch_live_odds()
        if raw_data:
            save_to_database(db, raw_data)
    finally:
        db.close()

"""
if __name__ == "__main__":
    db = SessionsLocal()
    try:
        # 1. Run the pipeline to pull data and process the new loops
        raw_data = fetch_live_odds()
        if raw_data:
            save_to_database(db, raw_data)

        # 2. Check the database counts afterwareds:
        total_matches = db.query(Match).count() # from "spreadsheet 1"
        total_odds = db.query(OddsHistory).count()    # from "spreadsheet 2"
        first_game = db.query(Match).first()

        print("\n" + "="*40)
        print(f"📊 LIVE DATABASE STATS:")
        print(f"Total Matches Stored: {total_matches}")
        print(f"Total Odds Entries Stored: {total_odds}")
        if first_game:
            print(f"Sample Game: {first_game.home_team} vs {first_game.away_team}")
            print(f"Odds logged for this sample game: {len(first_game.odds_history)}")
        print("="*40 + "\n")
    finally:
        db.close()
"""


"""
if __name__ == "__main__":
    db = SessionsLocal()
    try:
        # diagnostic test block:
        first_game = db.query(Match).first()
        if first_game:
            print("\n" + "="*40)
            print(f"🎉 DATABASE VERIFICATION SUCCESSFUL!")
            print(f"Game Profile: {first_game.home_team} vs {first_game.away_team}")
            print(f"Logged Odds entries: {len(first_game.odds_history)}")
            print("="*40 + "\n")
        else:
            print("\n⚠️ Connection worked, but the tables look empty. Fetching live data now...")
            raw_data = fetch_live_odds()
            if raw_data:
                save_to_database(db, raw_data)
    finally:
        db.close()
    
"""   

