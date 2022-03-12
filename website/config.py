from datetime import timedelta

from definition import ROOT_PATH

# Create dummy secrey key so we can use sesions
SECRET_KEY = "7561117fac624e9b392242aa5e1722a22c1fb5f94014e5a0920b24e66e63e365"
# Create in-memory database
DATABASE_FILE = 'database.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + ROOT_PATH + '/' + DATABASE_FILE
SQLALCHEMY_ECHO = True

#Flask session duration
PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
