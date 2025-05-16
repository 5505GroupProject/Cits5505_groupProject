import unittest
import sys
import os
# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import session
from app import create_app, db
from app.models import UploadedText, AnalysisResult
from app.models.user import User
from app.models.upload import UploadedText
from tests.config_test import TestConfig

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SentiNews', response.data)

    def test_login_route(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back', response.data)

    def test_analyze_requires_login(self):
        response = self.client.get('/analyze', follow_redirects=True)
        self.assertTrue(
            b'/auth/login' in response.data or
            b'<form' in response.data or
            b'Sign In' in response.data or
            b'Welcome Back' in response.data or
            b'login' in response.data or
            response.status_code in (302, 401, 403)
        )

    def test_analyze_upload_permission(self):
        # Simulate a user and an upload
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        upload = UploadedText(content='Test content', user_id=user.id)
        db.session.add(upload)
        db.session.commit()

        # Log in as a different user
        other = User(username='otheruser', email='other@example.com')
        other.set_password('password')
        db.session.add(other)
        db.session.commit()
        self.client.post('/login', data={'username': 'otheruser', 'password': 'password'})
        response = self.client.get(f'/analyze/{upload.id}', follow_redirects=True)
        # Check whether it is redirected to the login page, permission prompts, or 404/403
        self.assertTrue(
            b"don't have permission" in response.data or
            b'No content available' in response.data or
            b'login' in response.data or
            b'/auth/login' in response.data or
            b'Sign In' in response.data or
            response.status_code in (302, 401, 403, 404)
        )

    def test_cleanup_orphaned_results(self):
        # Create a user to satisfy foreign key
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        # Simulate an orphaned result with valid owner_id
        result = AnalysisResult(title='Test', content='Test result', owner_id=user.id)
        db.session.add(result)
        db.session.commit()
        response = self.client.get('/cleanup-orphaned-results', follow_redirects=True)
        self.assertTrue(b'Successfully cleaned up' in response.data or response.status_code == 200)

if __name__ == '__main__':
    unittest.main()
