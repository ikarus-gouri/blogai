import requests
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DjangoBackendService:
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            logger.info(f"Request successful: {response.status_code}")
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            raise Exception(f"Request to {url} timed out")
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            raise Exception(f"Could not connect to {url}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    def send_classification_result(self, blog_id: str, classifications: list) -> Dict[str, Any]:
        endpoint = "/api/classification/save/"
        payload = {"blog_id": blog_id, "classifications": classifications}
        return self._make_request("POST", endpoint, data=payload)
    
    def send_summary_result(self, blog_id: str, summary: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        endpoint = "/api/summary/save/"
        payload = {"blog_id": blog_id, "summary": summary, "metadata": metadata or {}}
        return self._make_request("POST", endpoint, data=payload)
    
    def fetch_blog_content(self, blog_id: str) -> Dict[str, Any]:
        endpoint = f"/api/blog/{blog_id}/"
        return self._make_request("GET", endpoint)
    
    def update_blog_status(self, blog_id: str, status: str) -> Dict[str, Any]:
        endpoint = f"/api/blog/{blog_id}/status/"
        payload = {"status": status}
        return self._make_request("PUT", endpoint, data=payload)
    
    def send_processing_result(self, blog_id: str, classifications: list, 
                              summary: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        endpoint = "/api/blog/process-result/"
        payload = {
            "blog_id": blog_id,
            "classifications": classifications,
            "summary": summary,
            "metadata": metadata or {}
        }
        return self._make_request("POST", endpoint, data=payload)
    
    def health_check(self) -> Dict[str, Any]:
        endpoint = "/api/health/"
        return self._make_request("GET", endpoint)


def get_backend_service(base_url: str = "http://localhost:8000") -> DjangoBackendService:
    return DjangoBackendService(base_url)
