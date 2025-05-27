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
        
        # Perform search with content type filtering
        results = research_tool.search_digital_fundraising(content_types=content_types)
        print(f"[RESEARCH] Number of results fetched: {len(results)}")
        
        # Process results and track which ones are new
        processed_results = []
        for result in results:
            # Map fields for frontend compatibility
            title = result.get('title', 'Untitled')
            content = result.get('snippet', '') or result.get('content', '') or ''
            content_type = result.get('type', 'article') or result.get('content_type', 'article')
            url = result.get('link', '') or result.get('url', '')
            
            # Check if resource already exists by URL
            existing = Resource.query.filter_by(url=url).first()
            
            if existing:
                # If it exists, add it to results with its database ID
                processed_results.append({
                    'id': existing.id,
                    'title': title,
                    'content_type': existing.content_type,
                    'url': url,
                    'content': existing.content,
                    'created_at': existing.created_at.isoformat() if existing.created_at else None,
                    'updated_at': existing.updated_at.isoformat() if existing.updated_at else None,
                    'is_new': False
                })
                print(f"[RESEARCH] Found existing resource: {title}")
            else:
                # If it's new, save it to database
                try:
                    resource = Resource(
                        title=title,
                        content_type=content_type,
                        url=url,
                        content=content,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(resource)
                    db.session.commit()
                    
                    # Add to results with is_new flag
                    processed_results.append({
                        **resource.to_dict(),
                        'is_new': True
                    })
                    print(f"[RESEARCH] Saved new resource: {title}")
                except Exception as e:
                    db.session.rollback()
                    print(f"[RESEARCH] Error saving resource {title}: {str(e)}")
                    # Still add to results even if save failed
                    processed_results.append({
                        'title': title,
                        'content_type': content_type,
                        'url': url,
                        'content': content,
                        'is_new': True,
                        'error': str(e)
                    })
        
        response = {
            'status': 'success',
            'results': processed_results
        }
        print('[RESEARCH][DEBUG] Response to frontend:', json.dumps(response, indent=2))
        return jsonify(response)
        
    except Exception as e:
        print(f"[RESEARCH][ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
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