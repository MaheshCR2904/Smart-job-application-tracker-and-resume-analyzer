from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/')
def index():
    """List all available job postings"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    # Build query
    query = {'is_active': True}
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'company': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    if job_type:
        query['job_type'] = job_type
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    
    # Get total count
    total = mongo.db.jobs.count_documents(query)
    
    # Get jobs with pagination
    jobs = list(mongo.db.jobs.find(query).sort('created_at', -1).skip((page-1)*per_page).limit(per_page))
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('jobs/index.html', 
                           jobs=jobs, 
                           page=page, 
                           total_pages=total_pages,
                           search=search,
                           job_type=job_type,
                           location=location)

@bp.route('/<job_id>')
def view(job_id):
    """View job details"""
    try:
        job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('jobs.index'))
        
        # Check if user has already applied
        has_applied = False
        if current_user.is_authenticated:
            application = mongo.db.applications.find_one({
                'job_id': job_id,
                'user_id': current_user.id
            })
            has_applied = bool(application)
        
        return render_template('jobs/view.html', job=job, has_applied=has_applied)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('jobs.index'))

@bp.route('/<job_id>/apply', methods=['POST'])
@login_required
def apply(job_id):
    """Apply for a job"""
    try:
        job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('jobs.index'))
        
        # Check if already applied
        existing = mongo.db.applications.find_one({
            'job_id': job_id,
            'user_id': current_user.id
        })
        if existing:
            flash('You have already applied for this job', 'info')
            return redirect(url_for('jobs.view', job_id=job_id))
        
        # Create application
        application_data = {
            'user_id': current_user.id,
            'job_id': str(job_id),
            'company_name': job.get('company', ''),
            'job_role': job.get('title', ''),
            'location': job.get('location', ''),
            'salary': job.get('salary', ''),
            'application_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'status': 'Applied',
            'notes': request.form.get('cover_letter', ''),
            'applied_at': datetime.utcnow()
        }
        
        mongo.db.applications.insert_one(application_data)
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job_id))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('jobs.index'))

# Admin/HR routes for managing jobs
@bp.route('/manage')
@login_required
def manage():
    """Manage job postings (admin/HR only)"""
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to manage jobs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    jobs = list(mongo.db.jobs.find().sort('created_at', -1))
    applications = list(mongo.db.applications.find({'job_id': {'$ne': None}}))
    return render_template('jobs/manage.html', jobs=jobs, applications=applications)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new job posting (admin/HR only)"""
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to create jobs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'company': request.form.get('company'),
            'location': request.form.get('location'),
            'salary': request.form.get('salary'),
            'job_type': request.form.get('job_type'),
            'description': request.form.get('description'),
            'requirements': request.form.get('requirements'),
            'benefits': request.form.get('benefits'),
            'application_deadline': request.form.get('application_deadline'),
            'is_active': True,
            'created_by': current_user.id,
            'created_at': datetime.utcnow()
        }
        
        # Validation
        if not data['title'] or not data['company']:
            flash('Title and company are required', 'error')
            return render_template('jobs/create.html', data=data)
        
        mongo.db.jobs.insert_one(data)
        flash('Job posting created successfully', 'success')
        return redirect(url_for('jobs.manage'))
    
    return render_template('jobs/create.html', data={})

@bp.route('/<job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(job_id):
    """Edit job posting (admin/HR only)"""
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to edit jobs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('jobs.manage'))
        
        if request.method == 'POST':
            data = {
                'title': request.form.get('title'),
                'company': request.form.get('company'),
                'location': request.form.get('location'),
                'salary': request.form.get('salary'),
                'job_type': request.form.get('job_type'),
                'description': request.form.get('description'),
                'requirements': request.form.get('requirements'),
                'benefits': request.form.get('benefits'),
                'application_deadline': request.form.get('application_deadline'),
                'is_active': 'is_active' in request.form,
                'updated_at': datetime.utcnow()
            }
            
            mongo.db.jobs.update_one({'_id': ObjectId(job_id)}, {'$set': data})
            flash('Job posting updated successfully', 'success')
            return redirect(url_for('jobs.manage'))
        
        return render_template('jobs/edit.html', job=job)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('jobs.manage'))

@bp.route('/<job_id>/delete', methods=['POST'])
@login_required
def delete(job_id):
    """Delete job posting (admin/HR only)"""
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to delete jobs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        mongo.db.jobs.delete_one({'_id': ObjectId(job_id)})
        flash('Job posting deleted successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('jobs.manage'))

@bp.route('/<job_id>/applicants')
@login_required
def applicants(job_id):
    """View applicants for a job (admin/HR only)"""
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to view applicants.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('jobs.manage'))
        
        # Get applications for this job
        applications = list(mongo.db.applications.find({'job_id': job_id}).sort('applied_at', -1))
        
        # Get user IDs from applications
        user_ids = [ObjectId(app['user_id']) for app in applications if app.get('user_id')]
        users = {str(u['_id']): u for u in mongo.db.users.find({'_id': {'$in': user_ids}})} if user_ids else {}
        
        return render_template('jobs/applicants.html', job=job, applications=applications, users=users)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('jobs.manage'))
