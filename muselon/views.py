from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from muselon import muselon, db, lm


@muselon.route('/')
def index():
	return render_template('index.html')
