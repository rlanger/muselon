from muselon import db
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


ROLE_USER = 0
ROLE_ADMIN = 1

class User(Base):

	__tablename__ = 'user_table'

	id = Column(Integer, primary_key = True)
	username = Column(String(64), unique = True)
	fullname = Column(String(240))
	email = Column(String(120))
	password = Column(String)
	role = Column(SmallInteger, default = ROLE_USER)
#	events_authored = db.relationship('Event', backref = 'author', lazy = 'dynamic')

	def __init__(self, name, password):
		self.username = name
		self.fullname = name
		self.password = password

	def __repr__(self):
		return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
		
	def is_anonymous(self):
		return False
		
	def get_id(self):
		return unicode(self.id)
		
	def __repr__(self):
		return '<User %r>' % (self.nickname)	
		

class Character(Base):

	__tablename__ = 'character_table'
	
	id = Column(Integer, primary_key = True)
	character_username = Column(String(64))
	character_fullname = Column(String(240))
	about = Column(String)
	
# Initialize database schema (create tables)
Base.metadata.create_all(engine)
