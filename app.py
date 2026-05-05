import os
from dotenv import load_dotenv
from flask import Flask
from database.db import init_db

from routes.auth import auth
from routes.property import property_bp
from routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret')
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'database.db')
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')

# INIT DATABASE
init_db()

# REGISTER ROUTES
app.register_blueprint(auth)
app.register_blueprint(property_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])
