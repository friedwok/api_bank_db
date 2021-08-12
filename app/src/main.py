from typing import Optional, List, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from src.database import Session
import src.bank_model as bank_model
import src.schemas as schemas
import src.crud as crud


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
	return "hash" + password

def get_db():
	db = Session()
	try:
		yield db
	finally:
		db.close()

def http_not_found(model_object: Any, subject: str, id: int):
	if model_object is None:
		raise HTTPException(status_code=404,
				detail="%s with id %d not found" % (subject, id)
			)

async def user_is_admin(db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
	user = await crud.get_user_by_email(db=db, user_email=current_user)
	if user.is_customer:
		raise HTTPException(status_code=403,
				detail="Sorry, you don't have access rights to this content"
				)
	return db

async def user_is_customer(db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
	user = await crud.get_user_by_email(db=db, user_email=current_user)
	if not user.is_customer:
		raise HTTPException(status_code=403,
				detail="Sorry, you don't have access rights to this content"
				)
	return db

def user_authorized(db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
	return db


# account, customer, product, branch: create, read, update, delete
# Separately we can create branch and product, for creating an account we need to have a customer.
# If we create a customer, we must already have a branch and products,
# and at the same time we must create an account.


#account
@app.post("/accounts/", response_model=schemas.Account)
async def create_account(account: schemas.AccountCreate, db: Session = Depends(user_is_admin)):
	customer = await crud.get_customer(db=db, customer_id=account.customer_id)
	http_not_found(customer, 'Customer', account.customer_id)
	return await crud.create_account(db=db, account=account)

@app.get("/accounts/{account_id}", response_model=schemas.Account)
async def read_account(account_id: int, db: Session = Depends(user_is_customer)):
	db_account = await crud.get_account(db=db, account_id=account_id)
	http_not_found(db_account, 'Account', account_id)
	return db_account

@app.get("/accounts/", response_model=List[schemas.Account])
async def read_accounts(db: Session = Depends(get_db)):
	db_accounts = await crud.get_accounts(db=db)
	return db_accounts

@app.post("/accounts/{account_id}", response_model=schemas.Account)
async def update_account(account: schemas.AccountUpdate, db: Session = Depends(user_is_admin)):
	acc = await crud.get_account(db=db, account_id=account.id)
	http_not_found(acc, 'Account', account.id)

	updated_account = await crud.update_account(db=db, account=account)
	return updated_account

@app.get("/accounts/delete/{account_id}", response_model=schemas.Account)
async def delete_account(account_id: int, db: Session = Depends(user_is_admin)):
	acc = await crud.get_account(db=db, account_id=account_id)
	http_not_found(acc, 'Account', account_id)
	acc = await crud.delete_account(db=db, account_id=account_id)
	return acc

#customer
@app.post("/customers/", response_model=schemas.Customer)
async def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(user_is_admin)):
	cust = await crud.get_customer_by_email(db=db, email=customer.email)
	if cust:
		raise HTTPException(status_code=409,
				detail="Customer with email %s already exists" % customer.email
				)
	branch = await crud.get_branch(db=db, branch_id=customer.branch_id)

	if branch is None:
		raise HTTPException(status_code=404,
				detail="Branch with id %d does not exists" % customer.branch_id
				)

	return await crud.create_customer(customer=customer, db=db)

@app.get("/customer/{customer_id}/", response_model=schemas.Customer)
async def read_customer(customer_id: int, db: Session = Depends(user_is_customer)):
	customer = await crud.get_customer(customer_id=customer_id, db=db)
	http_not_found(customer, 'Customer', customer_id)
	return customer

#this method - exception, according to the rule, admin and customer can't watch clients
@app.get("/customers/", response_model=List[schemas.Customer])
async def read_customers(db: Session = Depends(get_db)):
	return await crud.get_customers(db=db)

@app.post("/customers/{customer_id}", response_model=schemas.Customer)
async def update_customer(customer: schemas.CustomerUpdate, db: Session = Depends(user_is_admin)):
	cust = await crud.get_customer(db=db, customer_id=customer.id)
	http_not_found(cust, 'Customer', customer.id)

	return await crud.update_customer(db=db, customer=customer)

@app.post("/customer/{customer_id}/delete", response_model=schemas.Customer)
async def delete_customer(customer_id: int, db: Session = Depends(user_is_admin)):
	customer = await crud.get_customer(customer_id=customer_id, db=db)
	http_not_found(customer, 'Customer', customer_id)

	return await crud.delete_customer(customer_id=customer_id, db=db)

@app.post("/customer/{customer_id}/products/add/", response_model=List[schemas.Product])
async def add_products(customer_id: int, products: schemas.AddProduct, db: Session = Depends(user_is_admin)):
	customer = await crud.get_customer(customer_id=customer_id, db=db)
	http_not_found(customer, 'Customer', customer_id)
	for prod_id in products.product_ids:
		prod = await crud.get_product(product_id=prod_id, db=db)
		http_not_found(prod, 'Product', prod_id)

	return await crud.add_products(customer_id=customer_id, products=products, db=db)

@app.post("/customer/{customer_id}/products/delete/", response_model=List[schemas.Product])
async def delete_products(customer_id: int, products: schemas.AddProduct, db: Session = Depends(user_is_admin)):
	customer = await crud.get_customer(customer_id=customer_id, db=db)
	http_not_found(customer, 'Customer', customer_id)
	for prod_id in products.product_ids:
		prod = await crud.get_product(product_id=prod_id, db=db)
		http_not_found(prod, 'Product', prod_id)

	return await crud.delete_products(customer_id=customer_id, products=products, db=db)

@app.get("/customer/{customer_id}/balance/")
async def read_balance(customer_id: int, db: Session = Depends(user_is_customer)):
	return await crud.get_balance(customer_id=customer_id, db=db)



#branch
@app.post("/branch/", response_model=schemas.Branch)
async def create_branch(branch: schemas.BranchCreate, db: Session = Depends(user_is_admin)):
	# add a check after adding hybrid property
	# ...
	return await crud.create_branch(db=db, branch=branch)

@app.get("/branch/{branch_id}", response_model=schemas.Branch)
async def read_branch(branch_id: int, db: Session = Depends(user_authorized)):
	branch = await crud.get_branch(branch_id=branch_id, db=db)
	http_not_found(branch, 'Branch', branch_id)
	return branch

@app.get("/branches/", response_model=List[schemas.Branch])
async def read_branches(db: Session = Depends(user_authorized)):
	return await crud.get_branches(db)

@app.post("/branches/{branch_id}", response_model=schemas.Branch)
async def update_branch(branch: schemas.BranchUpdate, db: Session = Depends(user_is_admin)):
	br = await crud.get_branch(db=db, branch_id=branch.id)
	http_not_found(br, 'Branch', branch.id)
	return await crud.update_branch(db=db, branch=branch)

@app.get("/branches/delete/{branch_id}", response_model=schemas.Branch)
async def delete_branch(branch_id: int, db: Session = Depends(user_is_admin)):
	branch = await crud.get_branch(branch_id=branch_id, db=db)
	http_not_found(branch, 'Branch', branch_id)

	customers = db.query(bank_model.Customer).filter_by(branch_id=branch_id).all()
	if customers:
		raise HTTPException(status_code=400,
				detail="You can't remove the branch because it contains customers, " +
					"first remove the customers"
				)
	return await crud.delete_branch(branch_id=branch_id, db=db)

#product
@app.post("/product/", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(user_is_admin)):
	# add check for exist product in table
	prod = await crud.get_product_by_name(product_name=product.product_name, db=db)
	if prod:
		raise HTTPException(status_code=400,
				detail="Product %d already exists" % product.id)

	for customer_id in product.customer_ids:
		cust = await crud.get_customer(db=db, customer_id=customer_id)
		http_not_found(cust, 'Customer', customer_id)

	return await crud.create_product(db=db, product=product)

@app.get("/product/{product_id}", response_model=schemas.Product)
async def read_product(product_id: int, db: Session = Depends(user_authorized)):
	product = await crud.get_product(product_id=product_id, db=db)
	http_not_found(product, 'Product', product_id)

	return product

@app.get("/products/", response_model=List[schemas.Product])
async def read_products(db: Session = Depends(user_authorized)):
#async def read_products(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
	return await crud.get_products(db=db)

@app.post("/product/update/{product_id}", response_model=schemas.Product)
async def update_product(product: schemas.ProductUpdate, db: Session = Depends(user_is_admin)):
	prod = await crud.get_product(product_id=product.id, db=db)
	http_not_found(prod, 'Product', product.id)
	return await crud.update_product(db=db, product=product)


@app.post("/products/delete/{product_id}", response_model=schemas.Product)
async def delete_product(product_id: int, db: Session = Depends(user_is_admin)):
	product = await crud.get_product(product_id=product_id, db=db)
	http_not_found(product, 'Product', product_id)

	return await crud.delete_product(product_id=product_id, db=db)



@app.get("/users/me", response_model=schemas.User)
async def read_user_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	user = await crud.get_user_by_email(db, user_email=token)
	return user


@app.post("/token")
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
	user_dict = await crud.get_user_by_email(db, user_email=form_data.username)
	if not user_dict:
		raise HTTPException(status_code=401, detail="Incorrect username")
	if not hash_password(form_data.password) == user_dict.hashed_password:
		raise HTTPException(status_code=401, detail="Incorrect password")

	return {"access_token": user_dict.email, "token_type": "bearer"}
