from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, and_, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.schema import Sequence


SQL_DB_URL = 'postgresql://postgres:postgres@localhost:5432/projstagetest'

engine = create_engine(SQL_DB_URL, echo=True)

Session = sessionmaker(engine)

Base = declarative_base()


class Entity(Base):
	__tablename__ = 'FCT_ENTITY'

	ENTITY_ID_SEQ= Sequence('FCT_ENTITY_ENTITY_ID_SEQ', metadata=Base.metadata)
	ENTITY_ID = Column(Integer, ENTITY_ID_SEQ, server_default=ENTITY_ID_SEQ.next_value(), primary_key=True)
	#ENTITY_ID = Column(Integer, primary_key=True)
	ENTITY_TYPE_ID = Column(Integer, ForeignKey('ENTITY_TYPE.ENTITY_TYPE_ID'))
	ENTITY_NAME = Column(String)

class EntityType(Base):
	__tablename__ = 'ENTITY_TYPE'

	ENTITY_TYPE_ID = Column(Integer, primary_key=True)
	ENTITY_TYPE_LABEL = Column(String(255))

#class Link(Base):
#	__tablename__ = 'LINK'

#	LINK_ID = Column(Integer, primary_key=True)
	#ENTITY_SOURCE_ID = Column(Integer)
	#ENTITY_TARGET_ID = Column(Integer)

class Project(Entity):

	ENTITY_TYPE = relationship(
		'EntityType',
		primaryjoin=(
			and_(Entity.ENTITY_TYPE_ID == EntityType.ENTITY_TYPE_ID, Entity.ENTITY_TYPE_ID == 1)
		),
		innerjoin=True,
		lazy=False
	)

	STAGES = relationship(
		'ProjectStage',
		#primaryjoin=(
		#	and_(Entity.ENTITY_TYPE_ID == 1)
		#),
		foreign_keys="ProjectStage.ENTITY_SOURCE_ID",
		lazy=False
	)


class Stage(Entity):

	ENTITY_TYPE = relationship(
		'EntityType',
		primaryjoin=(
			and_(
				Entity.ENTITY_TYPE_ID == EntityType.ENTITY_TYPE_ID,
				Entity.ENTITY_TYPE_ID == 2
			)
		)
	)

class ProjectStage(Base):
	__tablename__ = 'link'

	LINK_ID = Column(Integer, primary_key=True)
	# С КАВЫЧКАМИ НЕ РАБОТАЕТ ВО ПЕРВЫХ
	# ВО-ВТОРЫХ КОГДА НАСЛЕДУЕТСЯ ОТ Link, ПАРАМЕТРЫ НЕ ПЕРЕОПРЕДЕЛЯЮТСЯ!!!
	ENTITY_SOURCE_ID = Column(Integer, ForeignKey("FCT_ENTITY.ENTITY_ID"))
	ENTITY_TARGET_ID = Column(Integer, ForeignKey(Stage.ENTITY_ID))
	STAGE_SPEC = relationship("Stage", foreign_keys=[ENTITY_TARGET_ID], lazy=False)
	#STAGE_SPEC = relationship("Stage", lazy=False)

Base.metadata.create_all(engine)

session = Session()

obj = session.query(Project).all()
for o in obj:
	print(jsonable_encoder(o))
