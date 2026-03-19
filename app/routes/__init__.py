# Routes package
from app.routes.auth import bp as auth_bp
from app.routes.applications import bp as applications_bp
from app.routes.resume import bp as resume_bp
from app.routes.main import bp as main_bp
from app.routes.admin import bp as admin_bp
from app.routes.hr import bp as hr_bp

__all__ = ['auth_bp', 'applications_bp', 'resume_bp', 'main_bp', 'admin_bp', 'hr_bp']
