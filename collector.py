import requests


def collect_videos(query, api_key, max_results=20):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": api_key,
        "maxResults": max_results,
        "type": "video"
    }

    response = requests.get(url, params=params).json()

    videos = []

    for item in response.get("items", []):
        snippet = item.get("snippet", {})

        videos.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "views": 0  # views not available here, safe default
        })

    return videos