from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, select, func
from sqlalchemy.ext.hybrid import hybrid_property

from src.database import Base, engine, Session


#bank database model
class Account(Base):
	__tablename__ = 'accounts'

	id = Column(Integer, primary_key=True)
	customer_id = Column(Integer, ForeignKey('customers.id'))
	money = Column(String(50))

	#customer = relationship('Customer', back_populates='account_ids')


customer_product = Table('customer_product', Base.metadata,
			Column('customer_id', ForeignKey('customers.id'), primary_key=True),
			Column('product_id', ForeignKey('products.id'), primary_key=True)
)


class Customer(Base):
	__tablename__ = 'customers'

	id = Column(Integer, primary_key=True)
	fullname = Column(String(100))
	city = Column(String(50))
	address = Column(String(100))
	#each customer has its own number, which is not repeated
	email = Column(String(100))

	#OneToMany relationship Customer <-> Accounts
	#account_ids = relationship('Account', back_populates='customer')
	account_ids = relationship('Account')

	#ManyToOne relationship Customer <-> Branches
	branch_id = Column(Integer, ForeignKey('branch.id'))
	#branch = relationship('Branch', back_populates='customers')

	#ManyToMany relationship Customers <-> Products
	#products = relationship('Product',
	#			secondary='customer_product',
	#			back_populates='customers')
	products = relationship('Product', secondary=customer_product)

	@hybrid_property
	def info(self):
		return 'Full name: {}, City: {}, Address: {}, E-mail: {}'\
			.format(self.fullname, self.city, self.address, self.email)

	#value like tuple (fullname, city, address, email)
	@info.setter
	def info(self, value):
		self.fullname = value[0]
		self.city = value[1]
		self.address = value[2]
		self.email = value[3]

	@hybrid_property
	def balance(self):
		#return sum(account.money for account in self.account_ids)
		full = ""
		i = 1
		for acc in self.account_ids[:-1]:
			full += 'Account {}: {}, '.format(i, acc.money)
			i += 1
		full += 'Account {}: {}'.format(i, acc.money)
		return full

	#@balance.expression
	#def balance(cls):
	#	return select(func.sum(Account.money)).\
	#		where(Account.customer_id==cls.id)


 
	def __repr__(self):
		return "<Customer(fullname='%s', city='%s', address='%s', email='%s', balance='%s')>" % \
			(self.fullname, self.city, self.address, self.email, self.balance)


class Product(Base):
	__tablename__ = 'products'

	id = Column(Integer, primary_key=True)
	product_name = Column(String(100), unique=True)
	#ManyToMany Product <-> Customer
	#customers = relationship('Customer',
	#			secondary='customer_product',
	#			back_populates='products')


class Branch(Base):
	__tablename__ = 'branch'

	id = Column(Integer, primary_key=True)
	city = Column(String(50))
	address = Column(String(50))

	customers = relationship('Customer')

	@hybrid_property
	def full_address(self):
		return self.city + ', ' + self.address

	#value should be tuple like (city, address)
	@full_address.setter
	def full_address(self, value):
		self.city = value[0]
		self.address = value[1]

#user model
class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	fullname = Column(String(100))
	email = Column(String(100), unique=True)
	hashed_password = Column(String(100))
	is_customer = Column(Boolean, default=False)
