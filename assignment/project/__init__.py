from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
from flask_wtf.csrf import CSRFProtect



db = SQLAlchemy()


def create_app():
    from .models import User
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    migrate = Migrate(app, db)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    
    db.init_app(app)
   
    with app.app_context():
        db.create_all()   
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, we use it in the query for the user
        return User.query.get(int(user_id))     
    # blueprint for auth routes in our app

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app



