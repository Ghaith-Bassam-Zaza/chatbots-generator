from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from CONSTANTS import WEB_DATABASE_URL, SECRET_KEY
import os

db = SQLAlchemy()
migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = WEB_DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid deprecation warnings
    db.init_app(app)
    migrate.init_app(app, db)  # Link Flask-Migrate with your app and db

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    from .models import User

    # Remove the `create_all` logic, as migrations handle this now
    with app.app_context():
        if not os.path.exists("migrations"):  # Check if migrations folder exists
            # Print a message prompting to initialize migrations
            print('Migrations not found. Run "flask db init", "flask db migrate", and "flask db upgrade".')

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
