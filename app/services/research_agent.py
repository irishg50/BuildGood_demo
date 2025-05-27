import os
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import PyPDF2
import io
import re

load_dotenv()

class ResearchAgent:
    def __init__(self):
        self.serp_api_key = os.getenv('SERP_API_KEY')
        if not self.serp_api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    def search_digital_fundraising(self, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for digital fundraising trends using Google Search API
        """
        search_params = {
            "engine": "google",
            "q": "latest trends in digital fundraising 2024 articles blogs case studies filetype:pdf",
            "api_key": self.serp_api_key,
            "num": num_results,
            "tbm": "nws",  # News search
            "sort_by": "date"  # Sort by date
        }

        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"Search API error: {results['error']}")

        compiled_results = []
        
        if "news_results" in results:
            for item in results["news_results"]:
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                    "snippet": item.get("snippet", ""),
                    "type": "article"
                }
                # Check if the link is a PDF
                if result["link"].lower().endswith('.pdf'):
                    result["type"] = "pdf"
                compiled_results.append(result)

        return compiled_results

    def download_pdf(self, url: str) -> Dict[str, Any]:
        """
        Download and process a PDF file
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Generate filename from URL
            filename = re.sub(r'[^\w\-_.]', '_', url.split('/')[-1])
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            filepath = os.path.join(self.download_dir, filename)
            
            # Save PDF
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Extract text from PDF
            pdf_text = ""
            try:
                pdf_file = io.BytesIO(response.content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
            except Exception as e:
                pdf_text = f"Error extracting PDF text: {str(e)}"
            
            return {
                "filename": filename,
                "filepath": filepath,
                "content": pdf_text[:2000] + "..." if len(pdf_text) > 2000 else pdf_text,
                "size": len(response.content)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "content": f"Error downloading PDF: {str(e)}"
            }

    def get_article_content(self, url: str) -> str:
        """
        Fetch and extract main content from an article URL
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get main content (this is a basic implementation)
            content = soup.get_text(separator=' ', strip=True)
            
            # Limit content length
            return content[:2000] + "..." if len(content) > 2000 else content
            
        except Exception as e:
            return f"Error fetching content: {str(e)}"

    def save_results(self, results: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save search results to a JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"digital_fundraising_research_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filename 