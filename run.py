#!/usr/bin/env python3
"""
Smart Job Application Tracker and Resume Analyzer
Main Application Entry Point
"""

# Add current directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT: Import platform fix FIRST to prevent WMI timeout with pymongo
import platform_fix

from app import create_app
from app.extensions import mongo
from flask_bcrypt import generate_password_hash
from datetime import datetime

# Create application instance
app = create_app()

@app.cli.command('create-admin')
def create_admin():
    """Create an admin user"""
    import click
    
    username = click.prompt('Username')
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True)
    
    # Check if admin already exists
    admin_exists = mongo.db.users.find_one({'is_admin': True})
    if admin_exists:
        click.echo('Admin user already exists!')
        return
    
    # Create admin user
    password_hash = generate_password_hash(password)
    user_data = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.utcnow(),
        'is_active': True,
        'is_admin': True
    }
    mongo.db.users.insert_one(user_data)
    click.echo(f'Admin user {username} created successfully!')

if __name__ == '__main__':
    # Get configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Run the application
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )
