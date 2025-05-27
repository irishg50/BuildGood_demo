from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the home page."""
    return render_template('main/index.html')

@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('main/about.html') 