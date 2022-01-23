"""
This file contains tests for testing the User model
"""
import unittest
import time
from app.models import User, AnonymousUser, Permission, Role
from app import db


class UserModelTestCase(unittest.TestCase):
    """
    This class contain functions for testing the User model
    """

    def test_password_setter(self):
        """
        Tests if a password hash is created once a user creates a password
        """
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """
        Tests if trying to access the user password will raise an error
        """
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """
        Tests if a password will be verified if the correct password is input
        and be unverified if a false password is input
        """
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_passwords_salts_are_random(self):
        """
        Tests that users with the same password have different password hashes
        """
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        """
        Tests that the proper confirmation token used to verify user accounts will be confirmed
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        """
        Tests that a false confirmation token used to verify user accounts will not be confirmed
        """
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        """
        Tests that confirmation tokens that have expired do not work
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        """
        Tests that the proper reset password token will be accepted and the password will change
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        """
        Tests that a false reset password token will not be accepted and the password will not change
        """
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    def test_user_role(self):
        """
        Tests that a default user with the 'User' role will have the proper permissions
        """
        u = User(email='john@example.com', password='test')
        self.assertTrue(u.can(Permission.VIEW))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_role(self):
        """
        Tests that an anonymous user will have the proper permissions
        """
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.VIEW))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_technician_role(self):
        """
        Tests that a user with the 'Technician' role will have the proper permissions
        """
        r = Role.query.filter_by(name='Technician').first()
        u = User(email='bob@example.com', password='test', role=r)
        self.assertTrue(u.can(Permission.VIEW))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_admin_role(self):
        """
        Tests that a user with the 'Administrator' role will have the proper permissions
        """
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='mark@example.com', password='test', role=r)
        self.assertTrue(u.can(Permission.VIEW))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.ADMIN))