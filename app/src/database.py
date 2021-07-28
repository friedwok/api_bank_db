from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCH_DB_URL = "postgresql://postgres:postgres@localhost:5432/bank_db"

engine = create_engine(SQLALCH_DB_URL)

Session = sessionmaker(bind=engine)

Base = declarative_base()
