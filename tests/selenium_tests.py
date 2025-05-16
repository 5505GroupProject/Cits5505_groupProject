from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import unittest
import os

class TestSelenium(unittest.TestCase):

    def setUp(self):
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver.exe')
        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.get('http://localhost:5000')

    def tearDown(self):
        self.driver.quit()

    def test_home_page_loads(self):
        self.assertIn('Home', self.driver.title)

    def test_login_page_loads(self):
        self.driver.get('http://localhost:5000/login')
        self.assertIn('Login', self.driver.title)

    def test_upload_page_navigation(self):
        self.driver.get('http://localhost:5000/upload')

        self.assertTrue('Upload' in self.driver.title or 'Login' in self.driver.title)

    def test_analyze_requires_login(self):
        self.driver.get('http://localhost:5000/analyze')
        self.assertTrue('Login' in self.driver.page_source or 'Sign In' in self.driver.page_source)

    def test_profile_requires_login(self):
        self.driver.get('http://localhost:5000/profile')
        self.assertTrue('Login' in self.driver.title or 'Sign In' in self.driver.page_source)

if __name__ == '__main__':
    unittest.main()
