import os
import json
from collections import Counter
import re

def analyze_reviews(file_path):
    with open(file_path, 'r') as f:
        reviews = json.load(f)

    # 1. Filter: < 3 stars
    filtered = [r for r in reviews if r['rating'] < 3]

    # 2. Group by category
    grouped = {}
    for r in filtered:
        cat = r['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(r)

    # Prepare keywords (simple tokenizer)
    def get_keywords(text):
        words = re.findall(r'\\w+', text.lower())
        # Filter generic words if desired
        return [w for w in words if len(w) > 3]

    results = {}
    for cat, items in grouped.items():
        avg_sentiment = sum(i['sentiment_score'] for i in items) / len(items)
        
        all_words = []
        for i in items:
            all_words.extend(get_keywords(i['review']))
        
        counts = Counter(all_words)
        top_3 = [word for word, count in counts.most_common(3)]
        
        results[cat] = {
            "average_sentiment": avg_sentiment,
            "top_3_keywords": top_3
        }

    return results

if __name__ == "__main__":
    # Expecting path as first argument if provided, otherwise default to a local path for testing
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'agent_workspace/reviews.json'
    print(json.dumps(analyze_reviews(path), indent=2))
