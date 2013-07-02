from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from werkzeug import check_password_hash, generate_password_hash
from muselon import muselon, db, lm
from muselon.forms import RegistrationForm, LoginForm
from muselon.models import User

@muselon.route('/')
def index():
	return render_template('index.html')


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
	