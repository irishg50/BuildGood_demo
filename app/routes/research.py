from flask import Blueprint, render_template, request, jsonify
from app.research_tool import ResearchTool
from app.models.resource import Resource
from app.extensions import db
import os
import json
import logging
from datetime import datetime

bp = Blueprint('research', __name__)

@bp.route('/')
def index():
    """Render the research page."""
    return render_template('research/index.html')

@bp.route('/analyze')
def analyze():
    """Render the analysis page."""
    return render_template('research/analyze.html')

@bp.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        content_types = data.get('content_types', [])
        
        # Log incoming request
        print(f"[RESEARCH] Received search request: query='{query}', content_types={content_types}")
        
        # Initialize research tool
        research_tool = ResearchTool()
        
        # Perform search with content type filtering and get GPT-4 analysis
        analysis = research_tool.search_digital_fundraising(content_types=content_types)
        print(f"[RESEARCH] Analysis completed")
        
        if analysis and analysis.get('summary'):
            return jsonify({
                'status': 'success',
                'summary': analysis['summary'],
                'raw_results': analysis['raw_results']
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to generate analysis'
            }), 500
            
    except Exception as e:
        print(f"[RESEARCH][ERROR] {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/analyze', methods=['POST'])
def analyze_resources():
    """Handle resource analysis requests."""
    try:
        data = request.get_json()
        resource_ids = data.get('resource_ids', [])
        analysis_type = data.get('analysis_type')
        
        if not resource_ids:
            return jsonify({'error': 'No resources selected'}), 400
        
        if not analysis_type:
            return jsonify({'error': 'No analysis type specified'}), 400
        
        # Get resources from database
        resources = Resource.query.filter(Resource.id.in_(resource_ids)).all()
        
        if not resources:
            return jsonify({'error': 'No resources found'}), 404
        
        # Initialize research tool
        research_tool = ResearchTool()
        
        # Prepare content for analysis
        content = "\n\n".join([
            f"Title: {r.title}\nContent: {r.content}\nSummary: {r.summary}"
            for r in resources
        ])
        
        return jsonify({
            'status': 'success',
            'analysis': content
        })
        
    except Exception as e:
        print(f"[RESEARCH][ERROR] {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500 