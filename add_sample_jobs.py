#!/usr/bin/env python3
"""
Script to add sample jobs to the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import platform fix first
import platform_fix

from app import create_app
from app.extensions import mongo
from datetime import datetime, timedelta

# Sample jobs data
sample_jobs = [
    {
        'title': 'Senior Python Developer',
        'company': 'TechCorp Solutions',
        'location': 'Bangalore, Karnataka',
        'salary': '₹15,00,000 - ₹25,00,000 per year',
        'job_type': 'Full-time',
        'description': '''We are looking for an experienced Python Developer to join our dynamic team. 
You will be responsible for designing, developing, and maintaining our web applications and APIs.

Key Responsibilities:
- Design and implement RESTful APIs
- Write clean, maintainable, and efficient code
- Collaborate with cross-functional teams
- Participate in code reviews and mentoring junior developers
- Contribute to architectural decisions''',
        'requirements': '''Required Skills:
- 3+ years of experience with Python
- Strong knowledge of Flask or Django
- Experience with RESTful API development
- Good understanding of database design (SQL and NoSQL)
- Experience with Git and version control
- Familiarity with cloud platforms (AWS/Azure/GCP)

Nice to have:
- Experience with microservices architecture
- Knowledge of containerization (Docker/Kubernetes)
- Experience with CI/CD pipelines''',
        'benefits': '''What We Offer:
- Competitive salary and benefits
- Flexible working hours
- Remote work options
- Health insurance
- Learning and development opportunities
- Annual team outings''',
        'application_deadline': (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'Full Stack JavaScript Developer',
        'company': 'WebFlow Innovations',
        'location': 'Hyderabad, Telangana',
        'salary': '₹12,00,000 - ₹20,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Join our team as a Full Stack JavaScript Developer and work on cutting-edge web applications.

Key Responsibilities:
- Develop responsive web applications using React/Angular and Node.js
- Design and implement database schemas
- Work with REST and GraphQL APIs
- Optimize application performance
- Write clean, documented code''',
        'requirements': '''Required Skills:
- 2+ years of experience in Full Stack development
- Strong proficiency in JavaScript/TypeScript
- Experience with React, Angular, or Vue.js
- Node.js backend development experience
- MongoDB or PostgreSQL experience
- Understanding of web security practices''',
        'benefits': '''What We Offer:
- Competitive compensation
- Work from home flexibility
- Health and dental insurance
- Stock options
- Professional development budget''',
        'application_deadline': (datetime.utcnow() + timedelta(days=25)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'Data Scientist',
        'company': 'Analytics Pro Pvt Ltd',
        'location': 'Pune, Maharashtra',
        'salary': '₹18,00,000 - ₹30,00,000 per year',
        'job_type': 'Full-time',
        'description': '''We are seeking a talented Data Scientist to help us extract insights from our data and build predictive models.

Key Responsibilities:
- Analyze large datasets to identify patterns and trends
- Build and deploy machine learning models
- Create data visualizations and reports
- Collaborate with business teams to understand requirements
- Present findings to stakeholders''',
        'requirements': '''Required Skills:
- Master's or PhD in Computer Science, Statistics, or related field
- 2+ years of experience in data science
- Proficiency in Python and R
- Experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Strong SQL skills
- Experience with data visualization tools''',
        'benefits': '''What We Offer:
- Excellent salary package
- Performance bonuses
- Flexible work arrangements
- Conference attendance support
- Research publication opportunities''',
        'application_deadline': (datetime.utcnow() + timedelta(days=20)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'DevOps Engineer',
        'company': 'CloudNine Technologies',
        'location': 'Chennai, Tamil Nadu',
        'salary': '₹14,00,000 - ₹22,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Looking for a DevOps Engineer to streamline our development and deployment processes.

Key Responsibilities:
- Manage CI/CD pipelines
- Implement and maintain cloud infrastructure
- Automate manual processes
- Monitor system performance and reliability
- Ensure security best practices''',
        'requirements': '''Required Skills:
- 3+ years of DevOps experience
- Strong knowledge of Docker and Kubernetes
- Experience with AWS, Azure, or GCP
- Proficiency in scripting (Bash, Python)
- Experience with configuration management tools (Ansible, Terraform)
- Knowledge of monitoring tools (Prometheus, Grafana)''',
        'benefits': '''What We Offer:
- Competitive salary
- Certification reimbursement
- Health insurance
- Paid time off
- Career growth opportunities''',
        'application_deadline': (datetime.utcnow() + timedelta(days=15)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'UI/UX Designer',
        'company': 'DesignHub Creative Agency',
        'location': 'Mumbai, Maharashtra',
        'salary': '₹8,00,000 - ₹15,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Create beautiful and intuitive user interfaces for our web and mobile applications.

Key Responsibilities:
- Design user interfaces and experiences
- Create wireframes, prototypes, and mockups
- Conduct user research and usability testing
- Collaborate with developers to implement designs
- Maintain design systems''',
        'requirements': '''Required Skills:
- 2+ years of UI/UX design experience
- Proficiency in Figma, Sketch, or Adobe XD
- Strong portfolio showcasing web and mobile designs
- Understanding of design principles
- Experience with user research methods
- Knowledge of HTML/CSS is a plus''',
        'benefits': '''What We Offer:
- Creative work environment
- Flexible hours
- Learning opportunities
- Design conference attendance
- Latest design tools and software''',
        'application_deadline': (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'Backend Developer (Java)',
        'company': 'Enterprise Solutions Inc',
        'location': 'Delhi NCR',
        'salary': '₹10,00,000 - ₹18,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Join our backend team to build scalable enterprise applications.

Key Responsibilities:
- Develop backend services using Java/Spring Boot
- Design and implement REST APIs
- Optimize database queries
- Write unit and integration tests
- Participate in code reviews''',
        'requirements': '''Required Skills:
- 2+ years of Java development experience
- Strong knowledge of Spring Boot framework
- Experience with MySQL/PostgreSQL
- Understanding of microservices
- Familiarity with Git and Maven/Gradle''',
        'benefits': '''What We Offer:
- Competitive salary
- Health insurance
- Casual dress code
- Snacks and beverages
- Team building events''',
        'application_deadline': (datetime.utcnow() + timedelta(days=21)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'Junior Python Developer',
        'company': 'StartUp India',
        'location': 'Remote',
        'salary': '₹4,00,000 - ₹8,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Great opportunity for freshers to kickstart their career in Python development.

Key Responsibilities:
- Assist in developing web applications
- Write and maintain code
- Fix bugs and issues
- Learn new technologies
- Collaborate with team members''',
        'requirements': '''Required Skills:
- Basic knowledge of Python
- Understanding of HTML/CSS
- Familiarity with databases
- Good problem-solving skills
- Eagerness to learn
- B.E/B.Tech or equivalent degree''',
        'benefits': '''What We Offer:
- Training and mentorship
- Flexible work from home
- Certificate after completion
- Performance-based promotions
- Friendly team environment''',
        'application_deadline': (datetime.utcnow() + timedelta(days=45)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
    {
        'title': 'Mobile App Developer (Flutter)',
        'company': 'AppVentures',
        'location': 'Bangalore, Karnataka',
        'salary': '₹10,00,000 - ₹16,00,000 per year',
        'job_type': 'Full-time',
        'description': '''Develop cross-platform mobile applications using Flutter.

Key Responsibilities:
- Build cross-platform mobile apps
- Collaborate with designers and backend developers
- Optimize app performance
- Fix bugs and implement new features
- Maintain code quality''',
        'requirements': '''Required Skills:
- 2+ years of mobile development experience
- Strong Flutter/Dart skills
- Experience with Firebase
- Understanding of mobile UI/UX
- Published apps in App Store/Play Store is a plus''',
        'benefits': '''What We Offer:
- Competitive package
- Latest MacBook/workstation
- Health insurance
- Gym membership
- Free snacks and drinks''',
        'application_deadline': (datetime.utcnow() + timedelta(days=18)).strftime('%Y-%m-%d'),
        'is_active': True,
    },
]

def add_jobs():
    """Add sample jobs to the database"""
    app = create_app()
    
    with app.app_context():
        # Always add jobs, overwriting or adding to existing
        for job in sample_jobs:
            job['created_at'] = datetime.utcnow()
            result = mongo.db.jobs.insert_one(job)
            print(f"Added: {job['title']} at {job['company']}")
        
        print(f"\nSuccessfully added {len(sample_jobs)} jobs to the database!")

if __name__ == '__main__':
    add_jobs()
