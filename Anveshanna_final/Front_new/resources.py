import os
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

def search_youtube_videos(query, max_results=5):
    """Search for top YouTube videos related to the given query."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query + " tutorial",
        "maxResults": max_results,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    videos = []
    for item in data.get("items", []):
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        videos.append((video_title, video_url))
    
    return videos

# Example usage:
skills = ["Machine Learning", "Python", "TensorFlow"]
for skill in skills:
    print(f"Top YouTube videos for {skill}:")
    videos = search_youtube_videos(skill)
    for title, url in videos:
        print(f"- {title}: {url}")
    print("\n")
