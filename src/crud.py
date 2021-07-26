from sqlalchemy.orm import Session
import src.bank_model as bank_model
import src.schemas as schemas
from sqlalchemy import func, select


async def get_user_by_email(db: Session, user_email: str):
	return db.query(bank_model.User).filter(bank_model.User.email==user_email).first()

async def get_customer_by_id(db: Session, customer_id: int):
	return db.query(bank_model.Customer).get(customer_id)

async def get_customer_by_email(db: Session, email: str):
	return db.query(bank_model.Customer).filter_by(email=email).first()

#account
async def create_account(db: Session, account: schemas.AccountCreate):
	acc = bank_model.Account(money=account.money, customer_id=account.customer_id)
	db.add(acc)
	db.commit()
	return acc

async def get_account(account_id: int, db: Session):
	return db.query(bank_model.Account).get(account_id)

async def get_accounts(db: Session):
	return db.query(bank_model.Account).all()

async def update_account(db: Session, account: schemas.AccountUpdate):
	Acc = bank_model.Account
	update_dict = {}

	#if account.customer_id:
	#	update_dict.update({Acc.customer_id: account.customer_id})
	if account.money:
		update_dict.update({Acc.money: account.money})

	if update_dict:
		db.query(Acc).filter_by(id=account.id).update(update_dict)
		db.commit()

	return await get_account(db=db, account_id=account.id)

async def delete_account(account_id: int, db: Session):
	acc = db.query(bank_model.Account).filter_by(id=account_id).first()
	db.query(bank_model.Account).filter_by(id=account_id).delete()
	db.commit()
	return acc

#branch
async def create_branch(db: Session, branch: schemas.BranchCreate):
	br = bank_model.Branch(city=branch.city, address=branch.address)
	db.add(br)
	db.commit()
	return br

async def get_branch(branch_id: int, db: Session):
	return db.query(bank_model.Branch).get(branch_id)

async def get_branches(db: Session):
	return db.query(bank_model.Branch).all()

async def update_branch(db: Session, branch: schemas.BranchUpdate):
	br = bank_model.Branch
	update_dict = {}

	if branch.city:
		update_dict.update({br.city: branch.city})
	if branch.address:
		update_dict.update({br.address: branch.address})

	#table 'customer' has ForeignKey 'branch_id', so if we update customer_ids, we update cust table
	#for customer_id in branch.customer_ids:
		#update_dict = {bank_model.Customer.branch_id: branch.id}
		#db.query(bank_model.Customer).filter_by(id=customer_id).update(update_dict)
	if update_dict:
		db.query(br).filter_by(id=branch.id).update(update_dict)

	db.commit()

	return await get_branch(db=db, branch_id=branch.id)

async def delete_branch(db: Session, branch_id: int):
	branch = db.query(bank_model.Branch).filter_by(id=branch_id).first()
	db.query(bank_model.Branch).filter_by(id=branch_id).delete()
	db.commit()
	return branch

#product
async def create_product(db: Session, product: schemas.ProductCreate):
	# first we create row in Product table
	prod = bank_model.Product(product_name=product.product_name)
	db.add(prod)
	# then we add it in customer_products
	for customer_id in product.customer_ids:
		customer = db.query(bank_model.Customer).filter_by(id=customer_id).first()
		customer.products.append(prod)
	db.commit()
	return prod

async def get_product(product_id: int, db: Session):
	return db.query(bank_model.Product).get(product_id)

async def get_product_by_name(product_name: str, db: Session):
	return db.query(bank_model.Product).filter_by(product_name=product_name).first()

async def get_products(db: Session):
	return db.query(bank_model.Product).all()

async def update_product(db: Session, product: schemas.ProductUpdate):
	pr = bank_model.Product
	update_dict = {}

	if product.product_name:
		update_dict.update({pr.product_name: product.product_name})
		db.query(pr).filter_by(id=product.id).update(update_dict)

	db.commit()

	return await get_product(product_id=product.id, db=db)

async def delete_product(product_id: int, db: Session):
	#first we delete row from customer_product table
	db.query(bank_model.customer_product).filter_by(product_id=product_id).delete()
	#then in 'Product table'
	product = db.query(bank_model.Product).filter_by(id=product_id).one()
	db.query(bank_model.Product).filter_by(id=product_id).delete()
	db.commit()
	return product

#customer
async def create_customer(db: Session, customer: schemas.CustomerCreate):
	cust = bank_model.Customer(**customer.dict())
	account = bank_model.Account(customer_id=id, money='0')
	cust.account_ids.append(account)
	db.add(cust)
	db.commit()

	return cust

async def get_customer(customer_id: int, db: Session):
	data = db.query(bank_model.Customer).get(customer_id)
	return data

async def get_customers(db: Session):
	return db.query(bank_model.Customer).all()

#fullname, city, address, email, branch_id
async def update_customer(db: Session, customer: schemas.CustomerUpdate):
	cust = bank_model.Customer
	update_dict = {}

	if customer.fullname:
		update_dict.update({cust.fullname: customer.fullname})
	if customer.city:
		update_dict.update({cust.city: customer.city})
	if customer.address:
		update_dict.update({cust.address: customer.address})
	if customer.email:
		update_dict.update({cust.email: customer.email})
	if customer.branch_id:
		update_dict.update({cust.branch_id: customer.branch_id})
	
	if update_dict:
		db.query(cust).filter_by(id=customer.id).update(update_dict)
	db.commit()
	
	resp = await get_customer(db=db, customer_id=customer.id)
	return resp


async def delete_customer(customer_id: int, db: Session):
	customer = await get_customer(customer_id=customer_id, db=db)
	#first we delete accounts associated with customer
	accounts = db.query(bank_model.Account).filter_by(customer_id=customer_id).delete()
	#then we delete a customer
	db.query(bank_model.Customer).filter_by(id=customer_id).delete()
	db.commit()

	return customer

async def add_products(customer_id: int, products: schemas.AddProduct, db: Session):
	customer = await get_customer(customer_id=customer_id, db=db)
	prods = []
	for prod_id in products.product_ids:
		product = await get_product(product_id=prod_id, db=db)
		prods.append(product)
		#customer.products.append(product)
	customer.products.extend(prods)
	db.commit()
	db.refresh(customer)

	return prods

async def delete_products(customer_id: int, products: schemas.AddProduct, db: Session):
	customer = await get_customer(customer_id=customer_id, db=db)
	prods = []
	for prod_id in products.product_ids:
		product = await get_product(product_id=prod_id, db=db)
		prods.append(product)
		customer.products.remove(product)
	db.commit()
	db.refresh(customer)

	return prods

async def read_balance(customer_id: int, db: Session):
	customer = await get_customer(customer_id=customer_id, db=db)
	return customer.balance

#import database

#session = database.Session()

#cust = session.query(bank_model.Customer).filter_by(id=5).first()
#cust = get_customer_by_email(email='alb@mail.ru', db=session)
#print(cust)
#prod1 = session.query(bank_model.Product).filter_by(id=1).first()
#prod2 = session.query(bank_model.Product).filter_by(id=2).first()
#customer.products.append(prod1)
#customer.products.append(prod2)
#session.commit()


