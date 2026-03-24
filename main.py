from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import mongo
from app.models.application import ApplicationModel
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    stats = ApplicationModel.get_statistics(mongo.db, current_user.id)
    
    # Get recent applications
    recent_apps = list(mongo.db.applications.find({'user_id': current_user.id})
                     .sort('created_at', -1)
                     .limit(5))
    
    # Get data for chart
    chart_data = {
        'labels': ['Applied', 'Interview', 'Rejected', 'Offer'],
        'data': [
            stats.get('Applied', 0),
            stats.get('Interview', 0),
            stats.get('Rejected', 0),
            stats.get('Offer', 0)
        ]
    }
    
    return render_template('main/dashboard.html',
                         stats=stats,
                         recent_apps=recent_apps,
                         chart_data=json.dumps(chart_data))

@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # In production, send email here
        flash('Message sent successfully!', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html')
