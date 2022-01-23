"""
This file initializes the 'main' blueprint and injects some functions to use in jinja2
"""
from flask import Blueprint
from ..models import Permission, User

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permissions():
    #injects Permission class into jinja2
    return dict(Permission=Permission)

@main.app_context_processor
def inject_enumerate():
    #injects enumerate function into jinja2
    return dict(enumerate=enumerate)

@main.app_context_processor
def inject_provider_lookup():
    #injects custom function into jinja2
    def provider_lookup(provider_id):
        #looks up a user based on their id
        user = User.query.filter_by(id=provider_id).first()
        return user.last_name + ', ' + user.first_name
    return dict(provider_lookup=provider_lookup)

from . import views, errors