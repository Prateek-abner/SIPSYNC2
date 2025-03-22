# youtube.py

import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
YOUTUBE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

def search_youtube(query, max_results=3):
    """
    Search YouTube for videos related to the query.
    """
    if not YOUTUBE_API_KEY:
        print("Warning: YouTube API key not found. Using mock data.")
        # Return mock data if API key is missing
        return [
            {
                "title": f"How to Make {query.title()}",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "thumbnail": "https://via.placeholder.com/480x360"
            },
            {
                "title": f"Benefits of {query.title()}",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "thumbnail": "https://via.placeholder.com/480x360"
            }
        ]
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            videos = []
            for item in data.get("items", []):
                video = {
                    "title": item["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
                }
                videos.append(video)
            return videos
    except Exception as e:
        print(f"YouTube API error: {e}")
    
    # Return empty list if there was an error
    return []
