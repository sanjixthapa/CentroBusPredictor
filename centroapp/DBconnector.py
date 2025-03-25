from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#db config
host="pi.cs.oswego.edu",
username="CSC380_25S_TeamA",#username
password="csc380_25s",#pass
database_name="CSC380_25S_TeamA"

db_url = f"mysql+pymysql://{username}:{password}@{host}/{database_name}"

engine = create_engine(db_url, echo=True)

