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
	return render_template('index2.html')



# Returns a JSON object containing all comments in the thread, sorted into comment blocks.
# A comment block consists of all comments made by a character without interruption.
# Comments are sorted into groups so that the author character's name can be shown just once per block.
@muselon.route('/thread/<threadId>', methods=['GET', 'POST'])
def return_comments(threadId):
	
	comments = db.session.query(Comment).all()

	thread = []	
	count = 0
	while (count < len(comments)):
		
		commentblock={"author": comments[count].author, "comments": []}
		thread.append(commentblock)
		commentblock["comments"].append(comments[count].serialize())
		count += 1
				
		while count < len(comments) and comments[count].author==comments[count-1].author:
		
			commentblock["comments"].append(comments[count].serialize())
			count += 1
	
	print (thread)
	return jsonify (json_list = thread)
	
@muselon.route('/characters/user/<userId>/world/<worldId>', methods=['GET', 'POST'])
def return_available_characters(userId, worldId):
	characters = db.session.query(Character).all()
	
	return jsonify (json_list = [character.serialize() for character in characters])


@muselon.route('/socket.io/<path:remaining>')
def socketio(remaining):
	socketio_manage(request.environ, {"/threadspace": ThreadNamespace}, request)
	return 'done'

class ThreadNamespace(BaseNamespace):
	def initialize(self):
		print "HELLO HELLO HELLO"

	def on_post(self, data):
		print "NEW POST: " + data 
		comment = Comment(data)
		comment.save()
		self.emit("updateComments")


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
	
# 	
# @muselon.route('/chat', methods=['GET', 'POST'])
# def chat():
# 	return render_template("chat.html")
# 
# # chat views
# @muselon.route('/chatlist')
# def rooms():
#     """
#     Homepage - lists all rooms.
#     """
#     context = {"rooms": ChatRoom.query.all()}
#     print "CONTEXT:"
#     print context
#     return render_template('chat/rooms.html', **context)
# 
# 
# @muselon.route('/<path:slug>')
# def room(slug):
#     """
#     Show a room.
#     """
#     context = {"room": get_object_or_404(ChatRoom, slug=slug)}
#     return render_template('chat/room.html', **context)
# 
# 
# @muselon.route('/create', methods=['POST'])
# def create():
#     """
#     Handles post from the "Add room" form on the homepage, and
#     redirects to the new room.
#     """
#     name = request.form.get("name")
#     if name:
#         room, created = get_or_create(ChatRoom, name=name)
#         return redirect(url_for('room', slug=room.slug))
#     return redirect(url_for('rooms'))
# 

# class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
#     nicknames = []
# 
#     def initialize(self):
#         self.logger = muselon.logger
#         self.log("Socketio session started")
#         #chatRoom 
# 
# 
# 
#     def log(self, message):
#         self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
# 
#     def on_join(self, room):
#         self.room = room
#         self.join(room)
#         return True
# 
#     def on_nickname(self, nickname):
#         self.log('Nickname: {0}'.format(nickname))
#         self.nicknames.append(nickname)
#         self.session['nickname'] = nickname
#         self.broadcast_event('announcement', '%s has connected' % nickname)
#         self.broadcast_event('nicknames', self.nicknames)
#         self.broadcast_event('announcement', 'PREVIOUS ACTIVITY HERE')
#         for comment in Comment.query.all():
# 			self.broadcast_event('announcement', comment.text)
# 			self.emit_to_room(self.room, 'msg_to_room', "NICK", comment.text)
#         return True, nickname
# 
#     def recv_disconnect(self):
#         # Remove nickname from the list.
#         self.log('Disconnected')
#         nickname = self.session['nickname']
#         self.nicknames.remove(nickname)
#         self.broadcast_event('announcement', '%s has disconnected' % nickname)
#         self.broadcast_event('nicknames', self.nicknames)
#         self.disconnect(silent=True)
#         return True
# 
#     def on_user_message(self, msg):
#         self.log('User message: {0}'.format(msg))
#         #self.emit_to_room(self.room, 'msg_to_room',
#         #    self.session['nickname'], msg)
#         self.emit_to_room(self.room, 'msg_to_room', self.session['nickname'], msg)
#         self.emit_to_room(self.room, 'msg_to_room', self.session['nickname'], msg)
#         #roomObj = db.session.query(ChatRoom).filter_by(name=self.room).first();
#         #roomObj = ChatRoom.query.filter_by(name="World One").first()
#         chatRoom = ChatRoom.query.filter_by(slug="world-one").first()
#         newComment = Comment(chatRoom, self.session['nickname'], msg)
#         self.log (newComment);
#         newComment.save()
#         
#         for comment in Comment.query.all():
# 			self.emit_to_room(self.room, 'msg_to_room', self.session['nickname'], msg)
# 			print("comment")
#         
#         return True
#        
#     # ON ROLL FATE 
#     def on_roll_fate(self, msg):
#     	self.log('Roll Fate: {0}'.format(msg))
#         self.emit_to_room(self.room, 'roll_fate',
#             self.session['nickname'], msg)


#@muselon.route('/socket.io/<path:remaining>')
#def socketio(remaining):
#    try:
#        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
#    except:
#        muselon.logger.error("Exception while handling socketio connection",
#                         exc_info=True)
#    return Response()