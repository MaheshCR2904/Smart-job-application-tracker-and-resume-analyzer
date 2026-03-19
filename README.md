# Smart Job Application Tracker and Resume Analyzer

A comprehensive full-stack web application for tracking job applications and analyzing resumes with AI-powered tools.

## 🚀 Features

### User Authentication
- User registration and login system
- Password hashing with Bcrypt
- Session management with Flask-Login
- Secure logout functionality

### Job Application Tracker
- Add, edit, and delete job applications
- Track company name, job role, location, salary
- Application status tracking (Applied, Interview, Rejected, Offer)
- Notes for each application
- Dashboard with statistics
- Search and filter applications
- CSV export functionality

### Resume Analyzer
- Upload resumes (PDF and DOCX supported)
- Extract text using PyPDF2 and python-docx
- Skills detection
- ATS (Applicant Tracking System) scoring
- Missing keywords identification
- Job description matching
- Improvement suggestions

### Additional Features
- Dark mode support
- Mobile responsive design
- Interactive charts with Chart.js
- Clean, modern UI

## 📁 Project Structure

```
smart_job_tracker/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── applications.py
│   │   ├── resume.py
│   │   └── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── application.py
│   │   └── resume.py
│   ├── utils/
│   │   └── user.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── main/
│   │   │   ├── index.html
│   │   │   ├── dashboard.html
│   │   │   ├── about.html
│   │   │   └── contact.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html
│   │   ├── applications/
│   │   │   ├── index.html
│   │   │   ├── new.html
│   │   │   ├── view.html
│   │   │   └── edit.html
│   │   └── resume/
│   │       ├── index.html
│   │       ├── analyze.html
│   │       ├── result.html
│   │       └── history.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── uploads/
├── run.py
├── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Flask-PyMongo** - MongoDB integration
- **Flask-Bcrypt** - Password hashing
- **Flask-Login** - Session management
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS variables
- **JavaScript (ES6+)** - Dynamic functionality
- **Chart.js** - Interactive charts
- **Font Awesome** - Icons

### Database
- **MongoDB** - NoSQL database

### PDF Processing
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX text extraction

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud)
- pip package manager

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/smart_job_tracker.git
cd smart_job_tracker
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Make sure MongoDB is running. You can:

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Server
# https://www.mongodb.com/try/download/community

# Or use Docker
docker run -d -p 27017:27017 mongo:latest
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://www.mongodb.com/atlas
2. Create cluster and get connection string
3. Set environment variable:
```bash
set MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/smart_job_tracker
```

### 5. Set Environment Variables

Create a `.env` file in the project root:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/smart_job_tracker
HOST=0.0.0.0
PORT=5000
```

### 6. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 🐳 Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MONGO_URI=mongodb://mongo:27017/smart_job_tracker
    depends_on:
      - mongo

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### 3. Build and Run

```bash
docker-compose up -d
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Nginx with Gunicorn

1. Install Nginx
2. Configure nginx with reverse proxy
3. Use systemd or supervisor to manage gunicorn

### Environment Variables for Production

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<strong-random-secret-key>
MONGO_URI=<your-mongodb-uri>
```

## 📊 MongoDB Collections

### Users Collection
```json
{
    "_id": ObjectId,
    "username": String,
    "email": String,
    "password_hash": String,
    "created_at": Date,
    "is_active": Boolean
}
```

### Applications Collection
```json
{
    "_id": ObjectId,
    "user_id": String,
    "company_name": String,
    "job_role": String,
    "location": String,
    "salary": String,
    "application_date": Date,
    "status": String,
    "notes": String,
    "created_at": Date,
    "updated_at": Date
}
```

### Resume Analysis Collection
```json
{
    "_id": ObjectId,
    "user_id": String,
    "filename": String,
    "analysis": {
        "text_length": Number,
        "word_count": Number,
        "detected_skills": [String],
        "keyword_frequency": [{String, Number}],
        "ats_score": {
            "score": Number,
            "percentage": Number,
            "suggestions": [String]
        }
    },
    "created_at": Date
}
```

## 🎨 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user
- `GET /auth/profile` - User profile

### Applications
- `GET /applications/` - List applications
- `POST /applications/new` - Create application
- `GET /applications/<id>` - View application
- `POST /applications/<id>/edit` - Update application
- `POST /applications/<id>/delete` - Delete application
- `GET /applications/export` - Export CSV

### Resume
- `GET /resume/` - Resume analyzer index
- `POST /resume/analyze` - Analyze resume
- `GET /resume/result/<id>` - View analysis
- `GET /resume/history` - Analysis history

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For support, email support@smartjobtracker.com or open an issue on GitHub.

---

Built with ❤️ for job seekers everywhere.
