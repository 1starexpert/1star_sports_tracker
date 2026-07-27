"""
Working on DB. Some notes:

Do not leave single data_base connection open forever.
We create a session factory that opens a connection 
whenever an API Endpoint needs to talk to the db. We 
close it instantly when the connection finishes. 

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

##Create the engine that communicates with Postgres:
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True ## check if connection is alive before using it

)
# 2. Create a session local factory. This creates temporary data base sessions):
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create the base class that all our future database will inherit from:
Base = declarative_base()

# 4. Create a dependency function that FASTAPI can use to inject DB sessions into the routes.

def get_db():
    '''
    notice yield db instead of return db. This is a python feature called a Generator.
    When a FastAPI route requests a database connection, FastAPI runs this function
    up until the yield line. It then hands the active database session over to the API
    code to read or write data. Then pauses. 

    Once your API route finishes sending the response back to the user's browser, FastAPI
    jumps back into this function and runs the code under the finally, calling the db.close().
    When this happens, the connection is closed, preventing potential crashes.
    '''
    db = SessionsLocal()
    try:
        yield db
    finally:
        db.close() # When the API request ends, guarantees the database connection closes safely

