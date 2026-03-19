"""
Smart Job Application Tracker and Resume Analyzer
Flask Application Factory
"""

from flask import Flask
from app.extensions import mongo, login_manager, bcrypt, csrf, cors
from app.config import config
from app.utils.user import User


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from app.extensions import mongo
    return User.get_by_id(mongo.db, user_id)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Set configuration
    config_name = config_name or 'default'
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    # csrf.init_app(app)  # Disabled - forms not using Flask-WTF
    cors.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Import blueprints after extensions are initialized
    from app.routes import auth_bp, applications_bp, resume_bp, main_bp, admin_bp, hr_bp
    from app.routes.jobs import bp as jobs_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    
    return app
