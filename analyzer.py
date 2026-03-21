from collections import Counter
import re


def clean_text(text):
    return str(text).lower()


def safe_int(x):
    try:
        return int(str(x).replace(",", ""))
    except:
        return 0


def extract_keywords(titles):
    words = []

    for title in titles:
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', title.lower())
        words.extend(tokens)

    stopwords = {
        "the","is","and","to","of","in","a","for","on","with",
        "this","that","you","your","how","what"
    }

    filtered = [w for w in words if w not in stopwords and len(w) > 2]

    return Counter(filtered)


def analyze_videos_with_custom(videos, criteria):
    analyzed = []
    titles = []

    for vid in videos:
        title = vid.get("title", "")
        channel = vid.get("channel", "")
        views = safe_int(vid.get("views", 0))

        title_lower = clean_text(title)

        score = 0
        keyword_counts = {}

        for key, words in criteria.items():
            count = sum(1 for w in words if w.lower() in title_lower)
            keyword_counts[key] = count
            score += count

        analyzed.append({
            "Video Title": title,
            "Channel Name": channel,
            "Views": views,
            **keyword_counts,
            "Relevance Score": score
        })

        titles.append(title)

    keyword_counter = extract_keywords(titles)
    top_keywords = keyword_counter.most_common(15)

    return analyzed, top_keywords