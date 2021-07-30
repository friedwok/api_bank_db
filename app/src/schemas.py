from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
	fullname: str
	email: str

	class Config:
		orm_mode = True


#account
class AccountBase(BaseModel):
	money: str


class AccountCreate(AccountBase):
	#customer: Optional[Customer] = None
	customer_id: int


class AccountUpdate(BaseModel):
	id: int
	money: Optional[str] = None

class Account(AccountBase):
	id: int
	customer_id: int

	class Config:
		orm_mode = True


#product
class ProductBase(BaseModel):
	product_name: str


class ProductCreate(ProductBase):
	customer_ids: List[int] = []


class ProductUpdate(ProductBase):
	id: int
	#customer_ids: List[int] = []


class Product(ProductBase):
	id: int

	class Config:
		orm_mode=True


#customer
class CustomerBase(BaseModel):
	fullname: str
	city: str
	address: str
	email: str


class CustomerCreate(CustomerBase):
	#account_ids: List[Account]
	branch_id: int


class CustomerUpdate(BaseModel):
	id: int
	fullname: Optional[str] = None
	city: Optional[str] = None
	address: Optional[str] = None
	email: Optional[str] = None
	branch_id: Optional[int] = None

class AddProduct(BaseModel):
	product_ids: List[int]


class Customer(CustomerBase):
	id: int
	branch_id: int
	balance: str
	#info: str

	class Config:
		orm_mode=True

#branch
class BranchBase(BaseModel):
	city: str
	address: str


class BranchCreate(BranchBase):
	#customers: List[Customer] = []
	pass


class BranchUpdate(BaseModel):
	id: int
	city: str = None
	address: str = None
	#customer_ids: List[int] = []


class Branch(BranchBase):
	id: int
	customers_: str

	class Config:
		orm_mode=True
