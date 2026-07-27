from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base

class Match(Base):
    """
    Spreadsheet 1: This is the "game matches" table. 
    This stores the static, unmoving profile details of a specifc game. 
    """
    __tablename__ = "matches" # Recall that this is a magic method / built in python function

    # We use the unique game ID that the Odds API gives every match:

    id = Column(String, primary_key=True, index=True)
    sport_key = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    commence_time = Column(DateTime, nullable=False)
    """
    Some notes:
    Nullable enforces that we never save any data rows with blank or missing columns 
    """

    # This creates a virtual link in Python allowing us to easily access
    # all historical odds row associated with a specific match profile
    odds_history = relationship("OddsHistory", back_populates ="match", cascade="all, delete-orphan")


class OddsHistory(Base):
    """
    Spreadsheet 2: The 'odds_history' table. 
    This is a continuous running log tracking every price movement.
    """
    __tablename__ = "odds_history"
    
    # Since multiple sportsbooks will log lines for the same game,
    # we let Postgres auto-increment a unique number (1,2,3...) for every row
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # The Foreign Key pointer that links this row back to matches.id
    match_id = Column(String, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    """
    ForeignKey helps us bind the match entries in Spreadsheet 1 (containing all of the
    basic match info) to Spreadsheet 2(containing all of the entries of updated changing
    odds). CASCADE deletes entries in Spreadsheet 2 that correspond to entries in
    Spreadsheet 1 when entries in Spreadsheet 1 are deleted. 
    """

    sportsbook = Column(String, nullable=False) # example: "DraftKings" "FanDuel"
    team_name = Column(String, nullable=False) # The team name that the price belongs to
    price = Column(Integer, nullable=False) # The moneyline odds number (ex: -100, 1500, etc...)
    fetched_at = Column(DateTime, nullable=False) # The precise timestamp our logger scraped this line


    # The matching virtual link back to the parent Match object
    match = relationship("Match", back_populates="odds_history")
