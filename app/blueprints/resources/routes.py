from flask import Blueprint, render_template, jsonify, request
from ...models.resource import Resource
from ...extensions import db

bp = Blueprint('resources', __name__)

@bp.route('/')
def index():
    resources = Resource.query.all()
    return render_template('resources/index.html', resources=resources)

@bp.route('/<int:resource_id>')
def view(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return render_template('resources/view.html', resource=resource)

@bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Implement file processing and resource creation
    return jsonify({'message': 'File upload endpoint - to be implemented'})

@bp.route('/<int:resource_id>/delete', methods=['DELETE'])
def delete(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    return jsonify({'message': 'Resource deleted successfully'}) 