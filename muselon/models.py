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

	__tablename__ = 'characters'
	
	id = Column(Integer, primary_key = True)
	name = Column(String)
	about = Column(String)
	
	def serialize(self):
		return {"name": self.name, "id": self.id}
	
class Comment(Base):
	__tablename__ = 'comments'

	id = Column (Integer, primary_key=True)
	#thread_id = Column (Integer, ForeignKey('chatrooms.id'))
	author_id = Column (Integer, ForeignKey('characters.id'))
	time = Column (DateTime, nullable=False)
	text = Column (String, nullable=False)
	
	def __init__(self, text, author_id):
		#self.world_id = world.id
		#self.nickname = nickname
		self.author_id = author_id
		self.time = datetime.datetime.now()
		self.text = text


	def __unicode__(self):
		return self.author + ": " + self.text

	def save(self, *args, **kwargs):
		db.session.add(self)
		db.session.commit()

	def serialize(self):
		return {"authorId": self.author_id, "datetime": self.time, "text": self.text}

class World(Base):

	__tablename__ = 'world_table'
	
	id = Column(Integer, primary_key = True)
	title = Column(String)
	description = Column(String)
	
	# public / private
	# custom styling
	# places/events -> posts
	
	
# chat models
# class ChatRoom(Base):
#     __tablename__ = 'chatrooms'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     slug = db.Column(db.String(50))
#     users = db.relationship('ChatUser', backref='chatroom', lazy='dynamic')
#     comments = db.relationship('Comment', backref='chatroom', lazy='dynamic')
# 
#     def __unicode__(self):
#         return self.name
# 
#     def get_absolute_url(self):
#         return url_for('room', slug=self.slug)
# 
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         db.session.add(self)
#         db.session.commit()
# 
# 
# class ChatUser(Base):
#     __tablename__ = 'chatusers'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     session = db.Column(db.String(20), nullable=False)
#     chatroom_id = db.Column(db.Integer, db.ForeignKey('chatrooms.id'))
# 
#     def __unicode__(self):
#         return self.name
# 
# #class Comment(Base):
# #	__tablename__ = 'comments'
# # 	id = Column (Integer, primary_key=True)
# # 	world_id = Column (Integer, ForeignKey('chatrooms.id'))
# # 	#user_id = Column (Integer, ForeignKey('chatusers.id'))
# # 	time = Column (DateTime, nullable=False)
# # 	text = Column (String, nullable=False)
# # 	
# # 	def __init__(self, world, nickname, text):
# # 		self.world_id = world.id
# # 		#self.nickname = nickname
# # 		self.text = text
# # 
# # 		self.time = datetime.datetime.now()
# # 
# # 	def __unicode__(self):
# # 		return self.text
# # 
# # 	def save(self, *args, **kwargs):
# # 		db.session.add(self)
# # 		db.session.commit()

# Initialize database schema (create tables)
def init_db():
	Base.metadata.create_all(engine)

#def init_db():
#    db.create_all(app=muselon)
