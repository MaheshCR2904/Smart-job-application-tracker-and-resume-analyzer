from datetime import datetime
from bson import ObjectId
import re
from flask import current_app

class ResumeAnalyzer:
    """Resume analyzer for extracting and analyzing resume content"""
    
    def __init__(self, app=None):
        self.app = app
        self.ats_keywords = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.ats_keywords = app.config.get('ATS_KEYWORDS', []) if app else []
    
    @staticmethod
    def extract_text_from_pdf(filepath):
        """Extract text from PDF file"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(filepath):
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(filepath)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text(self, filepath):
        """Extract text based on file extension"""
        ext = filepath.rsplit('.', 1)[-1].lower()
        if ext == 'pdf':
            return self.extract_text_from_pdf(filepath)
        elif ext in ['docx', 'doc']:
            return self.extract_text_from_docx(filepath)
        return ""
    
    def analyze_skills(self, text):
        """Detect skills from resume text"""
        text_lower = text.lower()
        detected_skills = []
        
        for keyword in self.ats_keywords:
            if keyword.lower() in text_lower:
                detected_skills.append(keyword)
        
        return list(set(detected_skills))
    
    def analyze_keywords(self, text):
        """Analyze keywords in resume"""
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['the', 'and', 'for', 'with', 'from', 'that', 'this', 
                          'have', 'been', 'will', 'would', 'could', 'should',
                          'their', 'there', 'which', 'what', 'when', 'where',
                          'work', 'working', 'job', 'experience', 'years']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
    
    def calculate_ats_score(self, text, job_description=None):
        """Calculate basic ATS score"""
        score = 0
        max_score = 100
        
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text_lower)
        unique_words = set(words)
        
        # Content length (20 points)
        if len(words) > 200:
            score += 15
        elif len(words) > 100:
            score += 10
        else:
            score += 5
        
        # Unique words ratio (20 points)
        if len(unique_words) > 50:
            score += 20
        elif len(unique_words) > 30:
            score += 15
        else:
            score += 10
        
        # Skills detection (30 points)
        skills = self.analyze_skills(text)
        skill_score = min(len(skills) * 3, 30)
        score += skill_score
        
        # Contact info detection (15 points)
        has_email = '@' in text and '.' in text
        has_phone = bool(re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', text))
        
        if has_email:
            score += 8
        if has_phone:
            score += 7
        
        # Format indicators (15 points)
        has_sections = any(section in text_lower for section in 
                          ['education', 'experience', 'skills', 'summary'])
        if has_sections:
            score += 15
        
        return {
            'score': min(score, max_score),
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'skills_found': len(skills),
            'total_keywords': len(self.ats_keywords),
            'suggestions': self.generate_suggestions(text, skills)
        }
    
    def generate_suggestions(self, text, detected_skills):
        """Generate improvement suggestions"""
        suggestions = []
        
        # Check for missing common skills
        missing_skills = []
        important_skills = ['python', 'javascript', 'sql', 'communication']
        for skill in important_skills:
            if skill not in detected_skills:
                missing_skills.append(skill)
        
        if missing_skills:
            suggestions.append(f"Consider adding these important skills: {', '.join(missing_skills)}")
        
        # Content length suggestion
        words = len(re.findall(r'\b[a-zA-Z]{2,}\b', text.lower()))
        if words < 200:
            suggestions.append("Your resume seems short. Consider adding more details about your experience and projects.")
        elif words > 1000:
            suggestions.append("Your resume might be too long. Consider condensing it to 1-2 pages.")
        
        # Action verbs suggestion
        action_verbs = ['achieved', 'developed', 'implemented', 'managed', 'created', 'led']
        if not any(verb in text.lower() for verb in action_verbs):
            suggestions.append("Use strong action verbs like 'achieved', 'developed', 'implemented' to describe your accomplishments.")
        
        return suggestions
    
    def match_with_job_description(self, resume_text, job_description):
        """Match resume with job description"""
        resume_words = set(re.findall(r'\b[a-zA-Z]{2,}\b', resume_text.lower()))
        job_words = set(re.findall(r'\b[a-zA-Z]{2,}\b', job_description.lower()))
        
        # Extract keywords from job description
        job_keywords = []
        for keyword in self.ats_keywords:
            if keyword.lower() in job_words:
                job_keywords.append(keyword)
        
        # Calculate match
        matched_keywords = []
        for keyword in job_keywords:
            if keyword.lower() in resume_words:
                matched_keywords.append(keyword)
        
        if job_keywords:
            match_percentage = (len(matched_keywords) / len(job_keywords)) * 100
        else:
            match_percentage = 0
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_keywords': matched_keywords,
            'missing_keywords': [k for k in job_keywords if k not in matched_keywords],
            'total_job_keywords': len(job_keywords)
        }
    
    def analyze_resume(self, filepath, job_description=None):
        """Complete resume analysis"""
        text = self.extract_text(filepath)
        
        if not text:
            return {
                'success': False,
                'error': 'Could not extract text from file'
            }
        
        skills = self.analyze_skills(text)
        keyword_freq = self.analyze_keywords(text)
        ats_result = self.calculate_ats_score(text, job_description)
        
        result = {
            'success': True,
            'text_length': len(text),
            'word_count': len(text.split()),
            'detected_skills': skills,
            'keyword_frequency': keyword_freq[:10],
            'ats_score': ats_result,
            'file_path': filepath
        }
        
        if job_description:
            match_result = self.match_with_job_description(text, job_description)
            result['job_match'] = match_result
        
        return result
    
    @staticmethod
    def save_analysis(db, user_id, filename, analysis_result):
        """Save resume analysis to database"""
        analysis_data = {
            'user_id': user_id,
            'filename': filename,
            'analysis': analysis_result,
            'created_at': datetime.utcnow()
        }
        result = db.resume_analysis.insert_one(analysis_data)
        return result.inserted_id
    
    @staticmethod
    def get_analyses(db, user_id, page=1, per_page=10):
        """Get all resume analyses for user"""
        skip = (page - 1) * per_page
        analyses = list(db.resume_analysis.find({'user_id': user_id})
                        .sort('created_at', -1)
                        .skip(skip)
                        .limit(per_page))
        
        total = db.resume_analysis.count_documents({'user_id': user_id})
        
        return {
            'analyses': analyses,
            'total': total,
            'page': page,
            'per_page': per_page
        }
