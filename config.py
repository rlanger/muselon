import os

# Enabling Flask-WTF cross-site request forgery prevention 
CSRF_ENABLED = True

# Secret key required by Flask
SECRET_KEY = 'ourlittlesecret'	# crypto token

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('HEROKU_POSTGRESQL_CYAN_URL') or "sqlite:////Users/cicero/hackerschool/project_muselon/test.db"

basedir = os.path.abspath(os.path.dirname(__file__))

print "DATABASE: %s" % SQLALCHEMY_DATABASE_URI