from flask import Blueprint

bp = Blueprint('resources', __name__)

from . import routes 