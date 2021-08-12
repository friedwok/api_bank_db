from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker

SQL_DB_URL = 'postgresql://mg:mg@10.129.0.31:5432/mg'

engine = create_engine(SQL_DB_URL)

Session = sessionmaker(bind=engine)

session = Session()

##
Base = declarative_base()

class TableOne(Base):
	__tablename__ = 'tableone'

	id = Column(Integer, primary_key=True)

Base.metadata.create_all(engine)

t1 = TableOne()
session.add(t1)
session.commit()

