from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

bp = Blueprint('hr', __name__, url_prefix='/hr')

def hr_required(f):
    """Decorator to require HR access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_hr', False) and not getattr(current_user, 'is_admin', False):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@hr_required
def index():
    """HR dashboard overview"""
    # Get statistics for HR view
    total_applications = mongo.db.applications.count_documents({})
    total_candidates = mongo.db.users.count_documents({'is_admin': False, 'is_hr': False})
    
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
    
    # Get candidates (non-admin, non-HR users)
    candidates = list(mongo.db.users.find({'is_admin': False, 'is_hr': False}).sort('created_at', -1).limit(10))
    
    return render_template('hr/index.html', 
                           total_applications=total_applications,
                           total_candidates=total_candidates,
                           status_counts=status_counts,
                           recent_applications=recent_applications,
                           candidates=candidates)

@bp.route('/candidates')
@hr_required
def candidates():
    """List all candidates"""
    candidates = list(mongo.db.users.find({'is_admin': False, 'is_hr': False}).sort('created_at', -1))
    return render_template('hr/candidates.html', candidates=candidates)

@bp.route('/candidates/<user_id>')
@hr_required
def view_candidate(user_id):
    """View candidate details"""
    try:
        candidate = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not candidate:
            flash('Candidate not found.', 'error')
            return redirect(url_for('hr.candidates'))
        
        # Get candidate's applications
        applications = list(mongo.db.applications.find({'user_id': user_id}).sort('created_at', -1))
        
        # Transform data to match template expectations
        for app in applications:
            app['company'] = app.get('company_name', '')
            app['position'] = app.get('job_role', '')
        
        # Get candidate's resume analyses
        resumes = list(mongo.db.resumes.find({'user_id': user_id}).sort('created_at', -1))
        
        return render_template('hr/view_candidate.html', candidate=candidate, applications=applications, resumes=resumes)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('hr.candidates'))

@bp.route('/applications')
@hr_required
def applications():
    """List all applications for HR review"""
    # Get filter parameters
    status = request.args.get('status')
    company = request.args.get('company')
    
    query = {}
    if status:
        query['status'] = status
    if company:
        query['company_name'] = {'$regex': company, '$options': 'i'}
    
    applications = list(mongo.db.applications.find(query).sort('created_at', -1))
    
    # Transform data to match template expectations
    for app in applications:
        app['company'] = app.get('company_name', '')
        app['position'] = app.get('job_role', '')
    
    return render_template('hr/applications.html', applications=applications, status=status, company=company)

@bp.route('/applications/<app_id>')
@hr_required
def view_application(app_id):
    """View application details for HR"""
    try:
        application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
        if not application:
            flash('Application not found.', 'error')
            return redirect(url_for('hr.applications'))
        
        # Get candidate info
        candidate = mongo.db.users.find_one({'_id': ObjectId(application['user_id'])})
        
        return render_template('hr/view_application.html', application=application, candidate=candidate)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('hr.applications'))

@bp.route('/applications/<app_id>/update-status', methods=['POST'])
@hr_required
def update_status(app_id):
    """Update application status"""
    try:
        application = mongo.db.applications.find_one({'_id': ObjectId(app_id)})
        if not application:
            flash('Application not found.', 'error')
            return redirect(url_for('hr.applications'))
        
        new_status = request.form.get('status')
        if new_status in ['Applied', 'Interview', 'Offer', 'Rejected', 'Pending']:
            mongo.db.applications.update_one(
                {'_id': ObjectId(app_id)},
                {'$set': {'status': new_status, 'status_updated_at': datetime.utcnow()}}
            )
            flash(f'Application status updated to {new_status}.', 'success')
        else:
            flash('Invalid status.', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('hr.view_application', app_id=app_id))

@bp.route('/resumes')
@hr_required
def resumes():
    """List all resume analyses"""
    resumes = list(mongo.db.resumes.find().sort('created_at', -1))
    return render_template('hr/resumes.html', resumes=resumes)

@bp.route('/resumes/<resume_id>')
@hr_required
def view_resume(resume_id):
    """View resume analysis details"""
    try:
        resume = mongo.db.resumes.find_one({'_id': ObjectId(resume_id)})
        if not resume:
            flash('Resume analysis not found.', 'error')
            return redirect(url_for('hr.resumes'))
        
        # Get candidate info
        candidate = mongo.db.users.find_one({'_id': ObjectId(resume['user_id'])})
        
        return render_template('hr/view_resume.html', resume=resume, candidate=candidate)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('hr.resumes'))

@bp.route('/search')
@hr_required
def search():
    """Search candidates and applications"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('hr.index'))
    
    # Search in users (candidates)
    candidates = list(mongo.db.users.find({
        'is_admin': False,
        'is_hr': False,
        '$or': [
            {'username': {'$regex': query, '$options': 'i'}},
            {'email': {'$regex': query, '$options': 'i'}}
        ]
    }))
    
    # Search in applications
    applications = list(mongo.db.applications.find({
        '$or': [
            {'company_name': {'$regex': query, '$options': 'i'}},
            {'job_role': {'$regex': query, '$options': 'i'}}
        ]
    }))
    
    # Transform data to match template expectations
    for app in applications:
        app['company'] = app.get('company_name', '')
        app['position'] = app.get('job_role', '')
    
    return render_template('hr/search.html', 
                           query=query, 
                           candidates=candidates, 
                           applications=applications)

@bp.route('/analytics')
@hr_required
def analytics():
    """HR Analytics - recruitment metrics"""
    # Application status distribution
    status_distribution = []
    for status in ['Applied', 'Interview', 'Offer', 'Rejected', 'Pending']:
        count = mongo.db.applications.count_documents({'status': status})
        status_distribution.append({'status': status, 'count': count})
    
    # Top companies by applications
    pipeline = [
        {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    top_companies = list(mongo.db.applications.aggregate(pipeline))
    
    # Applications over time (last 7 days)
    application_trend = []
    from datetime import timedelta
    for i in range(7):
        date = datetime.utcnow()
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date = date - timedelta(days=i)
        next_date = date + timedelta(days=1)
        count = mongo.db.applications.count_documents({
            'created_at': {'$gte': date, '$lt': next_date}
        })
        application_trend.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    application_trend.reverse()
    
    return render_template('hr/analytics.html', 
                           status_distribution=status_distribution,
                           top_companies=top_companies,
                           application_trend=application_trend)
