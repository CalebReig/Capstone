"""
This is the main file for the application.
FLASK_APP environment variable should be set to this file
"""
import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Patient

app = create_app(os.getenv('FLASK_CONFIG', 'default')) #creates the app with devault config = development
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """
    This function allows for objects associated with the application data base to be used
    in the flask shell.
    :return: Returns a dictionary linking objects with a reference name
    """
    return dict(db=db, User=User, Role=Role, Patient=Patient)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """
    This function loads the application tests from the command line
    :param test_names: Specific tests from the test classes
    """
    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names) #if specific tests are called
    else:
        tests = unittest.TestLoader().discover('tests') #else all tests are run from the 'tests' folder
    unittest.TextTestRunner(verbosity=2).run(tests)