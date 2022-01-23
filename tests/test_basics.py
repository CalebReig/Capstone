"""
This file contains application tests for basic tests
"""
import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    """
    This class tests the initializes a test config application and runs basic tests
    """
    def setup(self):
        """
        Initializes application in testing config
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()


    def tear_down(self):
        """
        Tears down application after testing is complete
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_app_exists(self):
        """
        Tests that the application exists/was created successfully
        """
        self.assertFalse(current_app is None)


    def test_app_is_testing(self):
        """
        Tests that the application is in testing configuration
        """
        self.assertTrue(current_app.config['TESTING'])