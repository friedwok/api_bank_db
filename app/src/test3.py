from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.schema import Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


Base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@localhost:5432/cart_item')
Session = sessionmaker(bind=engine)

class CartItem(Base):
	__tablename__ = 'cartitems'

	cart_id_seq = Sequence('cart_id_seq', metadata=Base.metadata)
	cart_id = Column(Integer, cart_id_seq, server_default=cart_id_seq.next_value(), primary_key=True)
	description = Column(String(40))
	#createdate = Column(DateTime)

#Base.metadata.create_all(engine)

from pydantic import BaseModel
from typing import List


class ItemCreate(BaseModel):
	#cart_id: int
	description: str
	#createdate: datetime

class Item(ItemCreate):
	cart_id: int
	#description: str
	#createdate: datetime


from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder


app = FastAPI()

session = Session()

@app.get('/items/', response_model=List[Item])
def get_items():
	data = session.query(CartItem).all()
	#print(data[0].description)
	#return session.query(CartItem).all()
	return jsonable_encoder(data)

@app.post('/items/', response_model=Item)
def create_item(item: ItemCreate):
	cart_item = CartItem(description=item.description)
	session.add(cart_item)
	session.commit()
	session.refresh(cart_item)
	return jsonable_encoder(cart_item)
