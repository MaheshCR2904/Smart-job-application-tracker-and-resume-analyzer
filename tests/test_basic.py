import pytest
from app import create_app

@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that index page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_about_page(client):
    """Test that about page loads successfully"""
    response = client.get('/about')
    assert response.status_code == 200

def test_contact_page(client):
    """Test that contact page loads successfully"""
    response = client.get('/contact')
    assert response.status_code == 200

def test_login_page(client):
    """Test that login page loads successfully"""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page(client):
    """Test that register page loads successfully"""
    response = client.get('/auth/register')
    assert response.status_code == 200

def test_dashboard_requires_login(client):
    """Test that dashboard redirects to login"""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_applications_requires_login(client):
    """Test that applications page redirects to login"""
    response = client.get('/applications/')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_resume_requires_login(client):
    """Test that resume page redirects to login"""
    response = client.get('/resume/')
    assert response.status_code == 302
    assert '/auth/login' in response.location
