from flask import url_for
from muselon import db
from muselon.utils import *
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI
import datetime

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# JJP: I just found out about this, but there's
# a package for enums, so you might consider using
# https://pypi.python.org/pypi/enum/ 
ROLE_USER = 0
ROLE_ADMIN = 1

DESCRIPTION = 0
DIALOGUE = 1

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

	__tablename__ = 'characters'
	
	id = Column(Integer, primary_key = True)
	name = Column(String)
	about = Column(String)
	
	# JJP: A lot of your queries could be simplifed if you
	# had a relationship between characters and comments.
	
	def serialize(self):
		return {"name": self.name, "id": self.id}
		
	def __init__(self, name):
		self.name = name
		
	def save(self, *args, **kwargs):
		db.session.add(self)
		db.session.commit()
	
class Comment(Base):
	__tablename__ = 'comments'

	id = Column (Integer, primary_key=True)
	#thread_id = Column (Integer, ForeignKey('threads.id'))
	author_id = Column (Integer, ForeignKey('characters.id'))
	time = Column (DateTime, nullable=False)
	text = Column (String, nullable=False)
	type = Column (SmallInteger, default = DESCRIPTION)

	
	def __init__(self, type, text, author_id):
		self.type = type
		self.text = text
		self.author_id = author_id
		self.time = datetime.datetime.now()


	def __unicode__(self):
		return self.author + ": " + self.text

	def save(self, *args, **kwargs):
		db.session.add(self)
		db.session.commit()

	def serialize(self):
		return {"authorId": self.author_id, "datetime": self.time, "text": self.text, "type":self.type}

class World(Base):

	__tablename__ = 'world_table'
	
	id = Column(Integer, primary_key = True)
	title = Column(String)
	description = Column(String)
	
# Initialize database schema (create tables)
def init_db():
	Base.metadata.create_all(engine)
