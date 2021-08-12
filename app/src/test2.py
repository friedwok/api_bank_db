from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQL_DB_URL = 'postgresql://postgres:postgres@localhost:5432/projstagetest1'

engine = create_engine(SQL_DB_URL)

Session = sessionmaker(bind=engine)

Base = declarative_base(engine)

class Table1(Base):
	__tablename__ = 'table1'

	ENT_ID = Column(Integer, primary_key=True)
	ENT_TYPE = Column(String(32))

#Base.metadata.create_all(engine)

session = Session()

obj = Table1(ENT_TYPE='asdasd')
print(obj.__dict__)

#session.add(obj)
#session.commit()

objs = session.query(Table1).all()
for o in objs:
	print(o.__dict__)
