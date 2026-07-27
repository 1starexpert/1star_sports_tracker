##search computer for .env file to load the api key: 
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ODDS_API_KEY: str
    PROJECT_NAME: str = "Sports Betting Analytics Dashboard"
    DATABASE_URL: str


    # Tells pydantic to look for .env file
    # Extra="ignore" tells Pydantic to not crash if there are other variables inside the .env file...
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


