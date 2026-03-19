import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/smart_job_tracker'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # Resume Analyzer Settings
    ATS_KEYWORDS = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust',
        'sql', 'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django',
        'flask', 'spring', 'express', 'mongodb', 'postgresql', 'mysql', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
        'agile', 'scrum', 'ci/cd', 'microservices', 'rest api', 'graphql',
        'machine learning', 'deep learning', 'data science', 'nlp', 'computer vision',
        'testing', 'unit testing', 'integration testing', 'tdd', 'bdd',
        'project management', 'leadership', 'communication', 'problem solving',
        'teamwork', 'collaboration', 'analytical', 'creative', 'innovative'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/smart_job_tracker'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/smart_job_tracker_test'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    MONGO_URI = os.environ.get('MONGO_URI')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
