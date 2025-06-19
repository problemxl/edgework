"""HTTP client for making API requests to NHL endpoints."""

import requests
from typing import Optional, Dict, Any


class SyncHttpClient:
    """Synchronous HTTP client for NHL API requests."""
    
    def __init__(self, user_agent: str = "EdgeworkClient/1.0"):
        """
        Initialize the HTTP client.
        
        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json'
        })
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request.
        
        Args:
            url: The URL to request
            params: Optional query parameters
            
        Returns:
            Response object
        """
        return self.session.get(url, params=params)
    
    def close(self):
        """Close the session."""
        self.session.close()
