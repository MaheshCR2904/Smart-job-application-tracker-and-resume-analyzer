from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import mongo
from app.models.resume import ResumeAnalyzer
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('resume', __name__, url_prefix='/resume')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'doc'}

@bp.route('/')
@login_required
def index():
    """Resume analyzer index"""
    result = ResumeAnalyzer.get_analyses(mongo.db, current_user.id)
    
    return render_template('resume/index.html',
                         analyses=result['analyses'],
                         total=result['total'])

@bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Analyze resume"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('resume.analyze'))
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('resume.analyze'))
        
        if file and allowed_file(file.filename):
            # Create upload directory if it doesn't exist
            upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Secure filename and save
            filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            try:
                # Analyze resume
                analyzer = ResumeAnalyzer(current_app)
                result = analyzer.analyze_resume(filepath, job_description)
                
                if result.get('success'):
                    # Save analysis to database
                    analysis_id = ResumeAnalyzer.save_analysis(
                        mongo.db,
                        current_user.id,
                        file.filename,
                        result
                    )
                    
                    flash('Resume analyzed successfully', 'success')
                    return render_template('resume/result.html',
                                         analysis=result,
                                         filename=file.filename,
                                         analysis_id=str(analysis_id))
                else:
                    flash(result.get('error', 'Failed to analyze resume'), 'error')
                    
            except Exception as e:
                flash(f'Error analyzing resume: {str(e)}', 'error')
            
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return redirect(url_for('resume.analyze'))
        else:
            flash('Invalid file type. Please upload PDF or DOCX file.', 'error')
    
    return render_template('resume/analyze.html')

@bp.route('/result/<analysis_id>')
@login_required
def view_result(analysis_id):
    """View previous analysis result"""
    from bson import ObjectId
    
    try:
        analysis = mongo.db.resume_analysis.find_one({
            '_id': ObjectId(analysis_id),
            'user_id': current_user.id
        })
        
        if not analysis:
            flash('Analysis not found', 'error')
            return redirect(url_for('resume.index'))
        
        return render_template('resume/result.html',
                             analysis=analysis['analysis'],
                             filename=analysis['filename'],
                             analysis_id=str(analysis['_id']))
    except Exception:
        flash('Invalid analysis ID', 'error')
        return redirect(url_for('resume.index'))

@bp.route('/match', methods=['POST'])
@login_required
def match_with_job():
    """Match resume with job description"""
    job_description = request.form.get('job_description')
    
    if not job_description:
        flash('Please provide a job description', 'error')
        return redirect(url_for('resume.analyze'))
    
    # Get latest resume analysis
    latest_analysis = mongo.db.resume_analysis.find_one(
        {'user_id': current_user.id},
        sort=[('created_at', -1)]
    )
    
    if not latest_analysis:
        flash('Please upload and analyze a resume first', 'error')
        return redirect(url_for('resume.analyze'))
    
    # Re-analyze with job description
    analyzer = ResumeAnalyzer(None)
    resume_text = latest_analysis['analysis'].get('text', '')
    
    if not resume_text:
        # Re-extract text if needed
        flash('Resume text not found. Please re-upload your resume.', 'error')
        return redirect(url_for('resume.analyze'))
    
    match_result = analyzer.match_with_job_description(resume_text, job_description)
    
    # Update analysis with job match
    mongo.db.resume_analysis.update_one(
        {'_id': latest_analysis['_id']},
        {'$set': {'job_match': match_result}}
    )
    
    return render_template('resume/result.html',
                         analysis=latest_analysis['analysis'],
                         filename=latest_analysis['filename'],
                         match_result=match_result,
                         analysis_id=str(latest_analysis['_id']))

@bp.route('/history')
@login_required
def history():
    """View analysis history"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    result = ResumeAnalyzer.get_analyses(mongo.db, current_user.id, page, per_page)
    
    return render_template('resume/history.html',
                         analyses=result['analyses'],
                         total=result['total'],
                         page=result['page'],
                         per_page=result['per_page'],
                         total_pages=result.get('total_pages', 1))

@bp.route('/delete/<analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Delete analysis"""
    from bson import ObjectId
    
    try:
        result = mongo.db.resume_analysis.delete_one({
            '_id': ObjectId(analysis_id),
            'user_id': current_user.id
        })
        
        if result.deleted_count > 0:
            flash('Analysis deleted successfully', 'success')
        else:
            flash('Analysis not found', 'error')
            
    except Exception as e:
        flash(f'Error deleting analysis: {str(e)}', 'error')
    
    return redirect(url_for('resume.history'))

@bp.route('/api/extract-text', methods=['POST'])
@login_required
def extract_text_api():
    """API endpoint to extract text from uploaded file"""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            analyzer = ResumeAnalyzer(None)
            text = analyzer.extract_text(filepath)
            
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'text': text[:5000],  # Limit response size
                'text_length': len(text)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400
