from flask import Blueprint, jsonify, request, render_template, send_from_directory
from ...services.research_agent import ResearchAgent
import os

bp = Blueprint('research', __name__)

@bp.route('/')
def index():
    return render_template('research.html')

@bp.route('/api/research/digital-fundraising', methods=['GET'])
def research_digital_fundraising():
    try:
        num_results = request.args.get('num_results', default=20, type=int)
        
        research_tool = ResearchAgent()
        results = research_tool.search_digital_fundraising(num_results=num_results)
        
        # Get content for each result
        for result in results:
            if result["link"]:
                if result["type"] == "pdf":
                    pdf_info = research_tool.download_pdf(result["link"])
                    result.update(pdf_info)
                else:
                    content = research_tool.get_article_content(result["link"])
                    result["content"] = content
        
        # Save results to file
        filename = research_tool.save_results(results)
        
        return jsonify({
            "status": "success",
            "message": f"Research completed and saved to {filename}",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@bp.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

@bp.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    agent = ResearchAgent()
    results = agent.search(query)
    return jsonify(results)

@bp.route('/analyze', methods=['POST'])
def analyze():
    resource_id = request.json.get('resource_id')
    if not resource_id:
        return jsonify({'error': 'No resource ID provided'}), 400
    
    agent = ResearchAgent()
    analysis = agent.analyze_resource(resource_id)
    return jsonify(analysis) 