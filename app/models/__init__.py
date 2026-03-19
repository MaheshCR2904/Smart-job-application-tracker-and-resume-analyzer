from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from app.config import config

mongo = PyMongo()
brypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.applications import bp as applications_bp
    from app.routes.resume import bp as resume_bp
    from app.routes.main import bp as main_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.hr import bp as hr_bp
    
    # Import jobs blueprint
    from app.routes.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(hr_bp)
    
    # Create upload directory
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
    
    # Setup login manager user loader
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        from app.utils.user import User
        try:
            user_data = mongo.db.users.find_one({'_id': user_id})
            if user_data:
                return User(user_data)
        except Exception:
            pass
        return None
    
    # Create indexes for better performance
    with app.app_context():
        mongo.db.users.create_index('email', unique=True)
        mongo.db.applications.create_index([('user_id', 1), ('created_at', -1)])
        mongo.db.resume_analysis.create_index('user_id')
    
    return app
