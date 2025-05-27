import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.models.resource import Resource
from app.extensions import db

bp = Blueprint('resources', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
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
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    title = request.form.get('title', file.filename)
    content_type = request.form.get('content_type', 'other')
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    resource = Resource(
        title=title,
        content_type=content_type,
        file_path=file_path,
        url=request.form.get('url')
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource uploaded successfully', 'id': resource.id})

@bp.route('/<int:resource_id>/delete', methods=['DELETE'])
def delete(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    if resource.file_path and os.path.exists(resource.file_path):
        os.remove(resource.file_path)
    
    db.session.delete(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource deleted successfully'})

@bp.route('/<int:resource_id>/download')
def download(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    if not resource.file_path or not os.path.exists(resource.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        resource.file_path,
        as_attachment=True,
        download_name=os.path.basename(resource.file_path)
    )

@bp.route('/<int:resource_id>/view_pdf')
def view_pdf(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    if not resource.file_path or not os.path.exists(resource.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(resource.file_path) 