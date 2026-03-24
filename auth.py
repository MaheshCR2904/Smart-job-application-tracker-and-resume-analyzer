from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import mongo
from flask_bcrypt import generate_password_hash, check_password_hash
from app.utils.user import User
from email_validator import validate_email, EmailNotValidError
from datetime import datetime


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not email:
            errors.append('Please enter a valid email address')
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                errors.append('Please enter a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create user
        password_hash = generate_password_hash(password)
        user = User.create(mongo.db, username, email, password_hash)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user_data = mongo.db.users.find_one({'email': email})
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user, remember=bool(remember))
            
            # Update last login
            mongo.db.users.update_one(
                {'_id': user.id},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            flash('Welcome back!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile"""
    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if username and username != current_user.username:
            mongo.db.users.update_one(
                {'_id': current_user.id},
                {'$set': {'username': username}}
            )
            flash('Username updated successfully', 'success')
        
        if current_password and new_password:
            user_data = mongo.db.users.find_one({'_id': current_user.id})
            if check_password_hash(user_data['password_hash'], current_password):
                new_hash = generate_password_hash(new_password)
                mongo.db.users.update_one(
                    {'_id': current_user.id},
                    {'$set': {'password_hash': new_hash}}
                )
                flash('Password updated successfully', 'success')
            else:
                flash('Current password is incorrect', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    password = request.form.get('password')
    
    user_data = mongo.db.users.find_one({'_id': current_user.id})
    
    if check_password_hash(user_data['password_hash'], password):
        # Delete all user data
        mongo.db.users.delete_one({'_id': current_user.id})
        mongo.db.applications.delete_many({'user_id': current_user.id})
        mongo.db.resume_analysis.delete_many({'user_id': current_user.id})
        
        logout_user()
        flash('Your account has been deleted', 'info')
        return redirect(url_for('main.index'))
    else:
        flash('Password is incorrect', 'error')
        return redirect(url_for('auth.profile'))

@bp.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Create initial admin user (only works if no admin exists)"""
    # Check if any admin exists
    admin_exists = mongo.db.users.find_one({'is_admin': True})
    
    if admin_exists:
        flash('Admin user already exists', 'info')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        admin_code = request.form.get('admin_code')
        
        # Admin creation code (you can change this)
        ADMIN_CREATE_CODE = 'admin123'
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not email:
            errors.append('Please enter a valid email address')
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                errors.append('Please enter a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if admin_code != ADMIN_CREATE_CODE:
            errors.append('Invalid admin creation code')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/create_admin.html')
        
        # Create admin user
        password_hash = generate_password_hash(password)
        from bson import ObjectId
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'is_active': True,
            'is_admin': True
        }
        mongo.db.users.insert_one(user_data)
        
        flash('Admin user created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/create_admin.html')
