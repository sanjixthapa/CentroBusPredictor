from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Database configuration
host = "pi.cs.oswego.edu"
username = "CSC380_25S_TeamA"
password = "csc380_25s"
database_name = "CSC380_25S_TeamA"

db_url = f"mysql+pymysql://{username}:{password}@{host}/{database_name}"

# Create engine
engine = create_engine(db_url, echo=True)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_db_session():
    """Return a new database session"""
    return Session()

def init_db():
    """Initialize database tables if they don't exist"""
    Base.metadata.create_all(engine)

def close_db_session(session):
    """Close the session properly"""
    try:
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()