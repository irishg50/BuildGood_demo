import os
import json
from datetime import datetime, timedelta
import requests
from serpapi import GoogleSearch
from urllib.parse import urlparse
import PyPDF2
import io
from dotenv import load_dotenv

load_dotenv()
print("Loaded Perplexity API Key:", os.getenv('PERPLEXITY_API_KEY'))

class ResearchTool:
    def __init__(self):
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.downloads_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)

    def search_youtube(self, query, max_results=5):
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print("[YOUTUBE][ERROR] YouTube API key not found in environment variables")
            return []
            
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": str(max_results),
            "key": api_key,
            "order": "relevance",
            "relevanceLanguage": "en",
            "videoEmbeddable": "true",
            "videoSyndicated": "true",
            "videoDuration": "medium"
        }
        
        try:
            print(f"[YOUTUBE][DEBUG] Making request to YouTube API with query: {query}")
            print(f"[YOUTUBE][DEBUG] Request URL: {url}")
            print(f"[YOUTUBE][DEBUG] Request params: {params}")
            response = requests.get(url, params=params)
            print(f"[YOUTUBE][DEBUG] Response status code: {response.status_code}")
            print(f"[YOUTUBE][DEBUG] Response headers: {response.headers}")
            response.raise_for_status()
            data = response.json()
            print(f"[YOUTUBE][DEBUG] Response data: {json.dumps(data, indent=2)}")
            
            if "error" in data:
                print(f"[YOUTUBE][ERROR] YouTube API error: {data['error']}")
                return []
                
            results = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                results.append({
                    "title": snippet["title"],
                    "link": f"https://www.youtube.com/watch?v={video_id}",
                    "snippet": snippet["description"],
                    "type": "video",
                    "date": snippet["publishedAt"]
                })
            print(f"[YOUTUBE][DEBUG] Found {len(results)} videos")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[YOUTUBE][ERROR] Request failed: {str(e)}")
            return []
        except Exception as e:
            print(f"[YOUTUBE][ERROR] Unexpected error: {str(e)}")
            return []

    def search_upcoming_webinars(self, max_results=5):
        """Search for upcoming webinars in the next two weeks."""
        # Calculate dates for the next two weeks
        today = datetime.utcnow()  # Use UTC time
        two_weeks_later = today + timedelta(days=14)
        
        # Format dates for the search query
        date_range = f"{today.strftime('%Y-%m-%d')}..{two_weeks_later.strftime('%Y-%m-%d')}"
        
        # Search query specifically for webinars - expanded to include more platforms and terms
        query = f"(digital fundraising OR nonprofit fundraising) (webinar OR virtual event OR online workshop) (register OR signup OR join) (eventbrite OR zoom OR gotowebinar OR hopin) {date_range}"
        print(f"[WEBINAR][DEBUG] Search query: {query}")
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "num": max_results,
            "as_qdr": "d14"  # Last 14 days
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        print(f"[WEBINAR][DEBUG] Raw results: {json.dumps(results, indent=2)}")
        
        webinars = []
        
        if "organic_results" in results:
            for item in results["organic_results"]:
                # Only include results that look like webinar registration pages
                if any(keyword in item.get("link", "").lower() for keyword in ["eventbrite", "webinar", "register", "event", "zoom", "gotowebinar", "hopin"]):
                    webinars.append({
                        "title": item.get("title", "Untitled"),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "type": "webinar",
                        "date": item.get("date", "")
                    })
        
        print(f"[WEBINAR][DEBUG] Found {len(webinars)} webinars")
        return webinars

    def search_digital_fundraising(self, content_types=None):
        """Search for digital fundraising resources across multiple sources."""
        if content_types is None:
            content_types = ["article", "pdf", "video"]
            
        results = []
        
        # Search for articles
        if "article" in content_types:
            articles = self.search_articles()
            results.extend(articles)
            
        # Search for PDFs
        if "pdf" in content_types:
            pdfs = self.search_pdfs()
            results.extend(pdfs)
            
        # Search for videos
        if "video" in content_types:
            videos = self.search_videos()
            results.extend(videos)
            
        return results

    def search_articles(self, max_results=5):
        """Search for articles about digital fundraising."""
        all_articles = []
        
        # First search: charity nonprofit focus
        query1 = "charity nonprofit digital fundraising articles blogs case studies"
        params1 = {
            "engine": "google",
            "q": query1,
            "api_key": self.serpapi_key,
            "num": max_results,
            "as_qdr": "d14"  # Last 14 days
        }
        
        search1 = GoogleSearch(params1)
        results1 = search1.get_dict()
        
        if "organic_results" in results1:
            for item in results1["organic_results"]:
                all_articles.append({
                    "title": item.get("title", "Untitled"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "type": "article",
                    "date": item.get("date", ""),
                    "source_query": "charity nonprofit"
                })
        
        # Second search: best practices focus
        query2 = "digital fundraising best practices articles blogs case studies"
        params2 = {
            "engine": "google",
            "q": query2,
            "api_key": self.serpapi_key,
            "num": max_results,
            "as_qdr": "d14"  # Last 14 days
        }
        
        search2 = GoogleSearch(params2)
        results2 = search2.get_dict()
        
        if "organic_results" in results2:
            for item in results2["organic_results"]:
                # Check if this URL is already in our results to avoid duplicates
                if not any(article["link"] == item.get("link", "") for article in all_articles):
                    all_articles.append({
                        "title": item.get("title", "Untitled"),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "type": "article",
                        "date": item.get("date", ""),
                        "source_query": "best practices"
                    })
        
        return all_articles

    def search_pdfs(self, max_results=5):
        """Search for PDF documents about digital fundraising."""
        all_pdfs = []
        
        # First search: charity nonprofit focus
        query1 = "charity nonprofit digital fundraising filetype:pdf"
        params1 = {
            "engine": "google",
            "q": query1,
            "api_key": self.serpapi_key,
            "num": max_results,
            "as_qdr": "d14"  # Last 14 days
        }
        
        search1 = GoogleSearch(params1)
        results1 = search1.get_dict()
        
        if "organic_results" in results1:
            for item in results1["organic_results"]:
                if item.get("link", "").lower().endswith('.pdf'):
                    all_pdfs.append({
                        "title": item.get("title", "Untitled"),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "type": "pdf",
                        "date": item.get("date", ""),
                        "source_query": "charity nonprofit"
                    })
        
        # Second search: best practices focus
        query2 = "digital fundraising best practices filetype:pdf"
        params2 = {
            "engine": "google",
            "q": query2,
            "api_key": self.serpapi_key,
            "num": max_results,
            "as_qdr": "d14"  # Last 14 days
        }
        
        search2 = GoogleSearch(params2)
        results2 = search2.get_dict()
        
        if "organic_results" in results2:
            for item in results2["organic_results"]:
                if item.get("link", "").lower().endswith('.pdf'):
                    # Check if this URL is already in our results to avoid duplicates
                    if not any(pdf["link"] == item.get("link", "") for pdf in all_pdfs):
                        all_pdfs.append({
                            "title": item.get("title", "Untitled"),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "type": "pdf",
                            "date": item.get("date", ""),
                            "source_query": "best practices"
                        })
        
        return all_pdfs

    def search_videos(self, max_results=5):
        """Search for videos about digital fundraising."""
        return self.search_youtube("digital fundraising best practices", max_results)

    def _perplexity_search(self, query, num_results):
        """Query Perplexity API for search results."""
        url = "https://api.perplexity.ai/search"
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "num_results": num_results
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            try:
                response.raise_for_status()
            except Exception as e:
                print(f"[PERPLEXITY][ERROR] {e}")
                print(f"[PERPLEXITY][RESPONSE] Status: {response.status_code}")
                print(f"[PERPLEXITY][RESPONSE] Body: {response.text}")
                return []
            data = response.json()
            results = []
            for item in data.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'type': item.get('type', 'article'),
                    'date': item.get('date', ''),
                    'source': item.get('source', 'perplexity')
                })
            return results
        except Exception as e:
            print(f"[PERPLEXITY][ERROR] {e}")
            return []

    def _enrich_results(self, results):
        """Enrich search results with additional information and analysis using Perplexity."""
        enriched_results = []
        for result in results:
            # Optionally, fetch content and summarize using Perplexity
            summary = self._perplexity_summarize(result['link']) if result.get('link') else ''
            result['summary'] = summary
            result['analyzed_at'] = datetime.now().isoformat()
            enriched_results.append(result)
        return enriched_results

    def _perplexity_summarize(self, url):
        """Use Perplexity API to summarize a web page."""
        api_url = "https://api.perplexity.ai/summarize"
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        payload = {"url": url}
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            try:
                response.raise_for_status()
            except Exception as e:
                print(f"[PERPLEXITY][SUMMARY][ERROR] {e}")
                print(f"[PERPLEXITY][SUMMARY][RESPONSE] Status: {response.status_code}")
                print(f"[PERPLEXITY][SUMMARY][RESPONSE] Body: {response.text}")
                return ''
            data = response.json()
            return data.get('summary', '')
        except Exception as e:
            print(f"[PERPLEXITY][SUMMARY][ERROR] {e}")
            return ''

    def save_results(self, results):
        """Save research results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"research_results_{timestamp}.json"
        filepath = os.path.join(self.downloads_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return filename

def main():
    try:
        research_tool = ResearchTool()
        
        # Search for digital fundraising trends
        print("Searching for digital fundraising trends...")
        results = research_tool.search_digital_fundraising()
        
        # Save results
        filename = research_tool.save_results(results)
        print(f"Results saved to {filename}")
        
        return results
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Minimal script to test Perplexity API key and endpoint
if __name__ == "__main__":
    api_key = os.getenv('PERPLEXITY_API_KEY')
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Summarize the latest research on digital fundraising trends for charities and nonprofits. "
        "Include recent articles, blogs, case studies, research papers, PDFs, and online commentary from the last two weeks. "
        "Include citations."
    )
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "stream": False
    }
    print("[TEST] Testing Perplexity API key and endpoint with /chat/completions...")
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"[TEST] Status: {resp.status_code}")
        print(f"[TEST] Body: {resp.text}")
        if resp.status_code == 200:
            result = resp.json()
            print("[TEST] Answer:\n", result["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"[TEST][ERROR] {e}")

if __name__ == "__main__":
    main() 