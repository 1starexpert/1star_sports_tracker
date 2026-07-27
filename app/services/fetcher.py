"""
httpx:

The asynchronous version of python's request library.

"""

import httpx
from app.core.config import settings

async def fetch_live_mlb_odds():
    """
    Asynchronously queries the Odds API for up to date MLB betting lines from 
    major US bookmarkers like DraftKings, FanDuel, etc... 
    """
    api_key = settings.ODDS_API_KEY
    sport = "baseball_mlb"
    regions = "us"
    markets = "h2h" ## money line market
    odds_format = "american"

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"

    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        # account for rate limit or API error:
        if response.status_code != 200:
            raise Exception(f"API Response ERROR {response.status_code}: {response.text}")
        
        return response.json()

