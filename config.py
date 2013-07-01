import os

# Secret key required by Flask
SECRET_KEY = 'ourlittlesecret'	# crypto token

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:////Users/cicero/hackerschool/project_muselon/test.db"

basedir = os.path.abspath(os.path.dirname(__file__))

print "DATABASE: %s" % SQLALCHEMY_DATABASE_URI