from flask import Flask, Response, request, session, g, redirect, url_for, \
	abort, render_template, flash, jsonify
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from gevent import monkey

from werkzeug import check_password_hash, generate_password_hash

from muselon import muselon, db, lm
from muselon.forms import RegistrationForm, LoginForm
from muselon.models import User, Comment, Character
from muselon.utils import *

monkey.patch_all()

TIME_STORE_FORMAT = '%Y-%m-%d %H:%M'
TIME_DISPLAY_FORMAT = '%d %b, %Y %H:%M'

@muselon.route('/')
def index():
	return render_template('index.html')



# JJP: Python style note: usually you put this sort of comment explaining a method in
# what's called a "docstring", which is just a multiline comment that's the first thing
# appearing in a method, like this:

@muselon.route('/thread/<threadId>', methods=['GET', 'POST'])
def return_comments(threadId):
	"""Returns a JSON object containing all comments in the thread, sorted into comment blocks.
	A comment block consists of all comments made by a character without interruption.
	Comments are sorted into groups so that the author character's name can be shown just once per block."""
	
	# JJP: This will
	
	# JJP: if your models are set up correctly, you should just be able to do:
	# Comment.query.all()
	comments = db.session.query(Comment).all()

	thread = []
	count = 0

	while (count < len(comments)):
	# JJP: iterating with while loops and comments is usually considered unpythonic
	# its often better to just use `for comment in comments`
	
		character = db.session.query(Character).get(comments[count].author_id)
		# Also if you set up a relationship between Characters and Comments, you can
		# just do somthing like `character = comment.character` nd avoid the big messy
		# query. See http://docs.sqlalchemy.org/en/rel_0_8/orm/relationships.html

		print character

		commentblock={"authorId": character.id, "author": character.name, "comments": []}
		thread.append(commentblock)
		commentblock["comments"].append(comments[count].serialize())
		count += 1
		
		# JJP: not sure if this is a good idea, but is it really necessary for the server to do
		# all this work to group things into blocks? Since the blocks are sort of logic having
		# to do with how the stuff is presented, I think it makes more sense to have the backend
		# just send data and let the JS on the client side decide how to display it (viz., in blocks)
		
		while count < len(comments) and comments[count].author_id==comments[count-1].author_id:
		
			commentblock["comments"].append(comments[count].serialize())
			count += 1
	
	print (thread)
	return jsonify (json_list = thread)
	
	
@muselon.route('/characters/user/<userId>/world/<worldId>', methods=['GET', 'PUT'])
def return_available_characters(userId, worldId):
	characters = db.session.query(Character).all()
	
	#JJP: I tend to define distinct routes for each HTTP method, but this may be a matter of taste
	if request.method == 'GET':
		return jsonify (json_list = [character.serialize() for character in characters])
		
	if request.method == 'PUT':
		#revisedjson = request.json_list
		print ("REQUEST.ARGS: ", request.args['name'])
		# JJP: Python style is to do underscores (new_character) rather than camel case (newCharacter)
		newCharacter = Character(request.args['name'])
		newCharacter.save()
		return render_template(url_for("return_available_characters"))
		


@muselon.route('/socket.io/<path:remaining>')
def socketio(remaining):
	socketio_manage(request.environ, {"/threadspace": ThreadNamespace}, request)
	return 'done'

class ThreadNamespace(BaseNamespace, BroadcastMixin):
	def initialize(self):
		print "ThreadNamespace socket initialized"

	def on_description_post(self, data):
		print ("on description post")
		print ("NEW POST: ", data) 

		comment = Comment(0, data["text"], data["charId"])
		comment.save()
		self.broadcast_event("updateComments")
		
	def on_dialogue_post(self, data):
		print ("on dialogue post")
		print ("NEW POST: ", data)
		comment = Comment(1, data["text"], data["charId"]) # and icon
		comment.save()
		self.broadcast_event("updateComments")

@muselon.route('/profile')
def userProfile():
	return render_template('profile.html')


#JJP: If you want to be RESTful, creating a new entity is usually a POST to
# the appropriate collection, here a POST to `/characters`. See
# https://blog.apigee.com/detail/restful_api_design
@muselon.route('/newCharacter', methods=['GET', 'POST'])
def newCharacter():
	character = Character(request.form["data"])
	character.save()
	
# JJP: This isn't a view, so it seems weird to have lodged in the middle of all these views
# I might put this in models or just in the package __init__ or something.
@lm.user_loader
def load_user(userid):
	return User.query.get(userid)

@muselon.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm(request.form)
	if form.validate_on_submit():
		#user = User(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data))
		user = User(form.name.data, password=generate_password_hash(form.password.data))
		db.session.add(user)
		db.session.commit()
		login_user(user)
		flash("Thanks for registering")
		return redirect(url_for("index"))
	return render_template("register.html", form=form)

# JJP: It also seems like you have a lot of methods that can be GETed or POSTed to
# but you don't actually dispatch on which it is.
@muselon.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		# we use werzeug to validate user's password
		if user and check_password_hash(user.password, form.password.data):
			# the session can't be modified as it's signed, 
			# it's a safe place to store the user id
			login_user(user, remember=form.remember.data)
			flash('Welcome %s' % user.fullname)
			return redirect(url_for('index'))
	return render_template("login.html", form=form)
	
@muselon.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))
	
