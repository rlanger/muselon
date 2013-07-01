from muselon import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

ROLE_USER = 0
ROLE_ADMIN = 1

class User(Base):

	__tablename__ = 'user_table'

	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), unique = True)
	email = db.Column(db.String(120), unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
#	events_authored = db.relationship('Event', backref = 'author', lazy = 'dynamic')

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
	