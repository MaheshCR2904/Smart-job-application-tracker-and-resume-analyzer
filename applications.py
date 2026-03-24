from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, Response
from flask_login import login_required, current_user
from app.extensions import mongo
from app.models.application import ApplicationModel
from bson import ObjectId
import csv
import io
from datetime import datetime

bp = Blueprint('applications', __name__, url_prefix='/applications')

@bp.route('/')
@login_required
def index():
    """List all applications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'status': request.args.get('status'),
        'company': request.args.get('company'),
        'search': request.args.get('search')
    }
    
    result = ApplicationModel.get_all(mongo.db, current_user.id, filters, page, per_page)
    
    return render_template('applications/index.html',
                         applications=result['applications'],
                         total=result['total'],
                         page=result['page'],
                         total_pages=result['total_pages'],
                         filters=filters)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new application"""
    # Only admin and HR users can add new applications
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_hr', False)):
        flash('You do not have permission to add applications.', 'error')
        return redirect(url_for('applications.index'))
    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name'),
            'job_role': request.form.get('job_role'),
            'location': request.form.get('location'),
            'salary': request.form.get('salary'),
            'application_date': request.form.get('application_date'),
            'status': request.form.get('status'),
            'notes': request.form.get('notes')
        }
        
        # Validation
        if not data['company_name'] or not data['job_role']:
            flash('Company name and job role are required', 'error')
            return render_template('applications/new.html', data=data)
        
        ApplicationModel.create(mongo.db, current_user.id, data)
        flash('Job application added successfully', 'success')
        return redirect(url_for('applications.index'))
    
    return render_template('applications/new.html', data={})

@bp.route('/<application_id>')
@login_required
def view(application_id):
    """View application details"""
    application = ApplicationModel.get_by_id(mongo.db, application_id, current_user.id)
    
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('applications.index'))
    
    return render_template('applications/view.html', application=application)

@bp.route('/<application_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(application_id):
    """Edit application"""
    application = ApplicationModel.get_by_id(mongo.db, application_id, current_user.id)
    
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('applications.index'))
    
    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name'),
            'job_role': request.form.get('job_role'),
            'location': request.form.get('location'),
            'salary': request.form.get('salary'),
            'application_date': request.form.get('application_date'),
            'status': request.form.get('status'),
            'notes': request.form.get('notes')
        }
        
        if ApplicationModel.update(mongo.db, application_id, current_user.id, data):
            flash('Application updated successfully', 'success')
            return redirect(url_for('applications.view', application_id=application_id))
        else:
            flash('Failed to update application', 'error')
    
    return render_template('applications/edit.html', application=application)

@bp.route('/<application_id>/delete', methods=['POST'])
@login_required
def delete(application_id):
    """Delete application"""
    if ApplicationModel.delete(mongo.db, application_id, current_user.id):
        flash('Application deleted successfully', 'success')
    else:
        flash('Failed to delete application', 'error')
    
    return redirect(url_for('applications.index'))

@bp.route('/statistics')
@login_required
def statistics():
    """Get statistics for chart"""
    stats = ApplicationModel.get_statistics(mongo.db, current_user.id)
    return jsonify(stats)

@bp.route('/export')
@login_required
def export():
    """Export applications as CSV"""
    try:
        csv_data = ApplicationModel.export_csv(mongo.db, current_user.id)
        
        if not csv_data:
            flash('No applications to export', 'info')
            return redirect(url_for('applications.index'))
        
        # Create CSV in memory
        output = io.StringIO()
        fieldnames = csv_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
        
        output.seek(0)
        
        # Create response with CSV content
        csv_content = output.getvalue()
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=applications_{datetime.now().strftime("%Y%m%d")}.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('applications.index'))
