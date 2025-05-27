from flask import Blueprint

bp = Blueprint('research', __name__)

from . import routes 