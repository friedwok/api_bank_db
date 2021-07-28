from setuptools import setup, find_packages


install_requires = [
	'fastapi[all]==0.65.2',
	'pydantic==1.8.2',
	'typing-extensions==3.10.0.0',
	#databases
	'SQLAlchemy==1.4.19',
	'psycopg2-binary'
]

setup(
	name='bank_app',
	version='1.0.0',
	description='A little bank API, python module, docker image.',
	packages=find_packages(),
	install_requires=install_requires,
	scripts=['bin/dev.sh']
)
