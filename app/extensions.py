"""
Flask Extensions
"""
# Import platform fix FIRST to prevent WMI timeout with pymongo on Windows
try:
    import platform_fix
except ImportError:
    # Fallback if platform_fix.py is not in path
    import sys
    import platform as _platform
    if sys.platform == 'win32':
        # Basic workaround if platform_fix not available
        _original_system = _platform.system
        _platform.system = lambda: 'Windows'

from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_cors import CORS

# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
cors = CORS()
