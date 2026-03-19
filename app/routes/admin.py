from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_admin', False):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@admin_required
def index():
    """Admin dashboard overview"""
    # Get statistics
    total_users = mongo.db.users.count_documents({})
    total_applications = mongo.db.applications.count_documents({})
    total_resumes = mongo.db.resumes.count_documents({})
    
    # Get recent users
    recent_users = list(mongo.db.users.find().sort('created_at', -1).limit(10))
    
    # Get application status counts
    status_counts = {}
    for status in ['Applied', 'Interview', 'Offer', 'Rejected', 'Pending']:
        status_counts[status] = mongo.db.applications.count_documents({'status': status})
    
    # Get recent applications
    recent_applications = list(mongo.db.applications.find().sort('created_at', -1).limit(10))
    
    # Transform data to match template expectations
    for app in recent_applications:
        app['company'] = app.get('company_name', '')
        app['position'] = app.get('job_role', '')
    
    return render_template('admin/index.html', 
                           total_users=total_users,
                           total_applications=total_applications,
                           total_resumes=total_resumes,
                           status_counts=status_counts,
                           recent_users=recent_users,
                           recent_applications=recent_applications)

@bp.route('/users')
@admin_required
def users():
    """List all users"""
    users = list(mongo.db.users.find().sort('created_at', -1))
    return render_template('admin/users.html', users=users)

@bp.route('/users/<user_id>')
@admin_required
def view_user(user_id):
    """View user details"""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        # Get user's applications
        applications = list(mongo.db.applications.find({'user_id': user_id}).sort('created_at', -1))
        
        # Transform data to match template expectations
        for app in applications:
            app['company'] = app.get('company_name', '')
            app['position'] = app.get('job_role', '')
        
        # Get user's resume analyses
        resumes = list(mongo.db.resumes.find({'user_id': user_id}).sort('created_at', -1))
        
        return render_template('admin/view_user.html', user=user, applications=applications, resumes=resumes)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/users/<user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        # Prevent removing own admin status
        if user_id == current_user.id:
            flash('You cannot remove your own admin status.', 'error')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        new_admin_status = not user.get('is_admin', False)
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_admin': new_admin_status}})
        
        status = 'promoted to' if new_admin_status else 'demoted from'
        flash(f'User {status} admin successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))

@bp.route('/users/<user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_active(user_id):
    """Toggle active status for a user"""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        # Prevent deactivating yourself
        if user_id == current_user.id:
            flash('You cannot deactivate your own account.', 'error')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        new_active_status = not user.get('is_active', True)
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_active': new_active_status}})
        
        status = 'deactivated' if not new_active_status else 'activated'
        flash(f'User {status} successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))

@bp.route('/users/<user_id>/toggle-hr', methods=['POST'])
@admin_required
def toggle_hr(user_id):
    """Toggle HR status for a user"""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))
        
        new_hr_status = not user.get('is_hr', False)
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_hr': new_hr_status}})
        
        status = 'granted HR access to' if new_hr_status else 'removed HR access from'
        flash(f'User {status} successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_user', user_id=user_id))

@bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        if user_id == current_user.id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.users'))
        
        # Delete user's applications
        mongo.db.applications.delete_many({'user_id': user_id})
        
        # Delete user's resumes
        mongo.db.resumes.delete_many({'user_id': user_id})
        
        # Delete user
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@bp.route('/applications')
@admin_required
def applications():
    """List all applications"""
    applications = list(mongo.db.applications.find().sort('created_at', -1))
    
    # Transform data to match template expectations
    for app in applications:
        app['company'] = app.get('company_name', '')
        app['position'] = app.get('job_role', '')
    
    return render_template('admin/applications.html', applications=applications)

@bp.route('/applications/<app_id>')
@admin_required
def view_application(app_id):
    """View application details"""
    try:
        application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
        if not application:
            flash('Application not found.', 'error')
            return redirect(url_for('admin.applications'))
        
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(application['user_id'])})
        
        return render_template('admin/view_application.html', application=application, user=user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.applications'))

@bp.route('/applications/<app_id>/delete', methods=['POST'])
@admin_required
def delete_application(app_id):
    """Delete an application"""
    try:
        mongo.db.applications.delete_one({'_id': ObjectId(app_id)})
        flash('Application deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.applications'))

@bp.route('/resumes')
@admin_required
def resumes():
    """List all resume analyses"""
    resumes = list(mongo.db.resumes.find().sort('created_at', -1))
    return render_template('admin/resumes.html', resumes=resumes)

@bp.route('/resumes/<resume_id>')
@admin_required
def view_resume(resume_id):
    """View resume analysis details"""
    try:
        resume = mongo.db.resumes.find_one({'_id': ObjectId(resume_id)})
        if not resume:
            flash('Resume analysis not found.', 'error')
            return redirect(url_for('admin.resumes'))
        
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(resume['user_id'])})
        
        return render_template('admin/view_resume.html', resume=resume, user=user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.resumes'))

@bp.route('/resumes/<resume_id>/delete', methods=['POST'])
@admin_required
def delete_resume(resume_id):
    """Delete a resume analysis"""
    try:
        mongo.db.resumes.delete_one({'_id': ObjectId(resume_id)})
        flash('Resume analysis deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.resumes'))

@bp.route('/analytics')
@admin_required
def analytics():
    """Analytics overview"""
    # User growth over time
    user_growth = []
    for i in range(7):
        date = datetime.utcnow()
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        date = date - timedelta(days=i)
        next_date = date + timedelta(days=1)
        count = mongo.db.users.count_documents({
            'created_at': {'$gte': date, '$lt': next_date}
        })
        user_growth.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    user_growth.reverse()
    
    # Application status distribution
    status_distribution = []
    for status in ['Applied', 'Interview', 'Offer', 'Rejected', 'Pending']:
        count = mongo.db.applications.count_documents({'status': status})
        status_distribution.append({'status': status, 'count': count})
    
    # Top companies
    pipeline = [
        {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    top_companies = list(mongo.db.applications.aggregate(pipeline))
    
    return render_template('admin/analytics.html', 
                           user_growth=user_growth,
                           status_distribution=status_distribution,
                           top_companies=top_companies)
