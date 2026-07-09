from datetime import datetime, timezone
import requests


class HackerNewsAPIScraper:
    source_name = "hackernews"

    def __init__(self, keyword: str, max_pages: int = 1, headless: bool = True):
        self.keyword = keyword
        self.max_pages = max_pages
        self.headless = headless

    def close(self):
        pass

    def _score(self, hit: dict) -> int:
        points = hit.get("points") or 0
        comments = hit.get("num_comments") or 0
        score = 25
        if points >= 500:
            score += 35
        elif points >= 100:
            score += 25
        elif points >= 10:
            score += 10
        if comments >= 100:
            score += 25
        elif comments >= 20:
            score += 15
        if hit.get("url"):
            score += 15
        return min(score, 100)

    def scrape(self) -> list[dict]:
        results = []
        for page in range(0, self.max_pages):
            response = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": self.keyword, "tags": "story", "page": page, "hitsPerPage": 20},
                headers={"User-Agent": "LeadFlow-Pro-Portfolio-Project"},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            for hit in data.get("hits", []):
                title = hit.get("title") or hit.get("story_title") or "Untitled"
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                results.append({
                    "title": title,
                    "name": title,
                    "company": hit.get("author", ""),
                    "description": f"HN story by {hit.get('author', '')}. Points: {hit.get('points', 0)}. Comments: {hit.get('num_comments', 0)}.",
                    "url": url,
                    "source": self.source_name,
                    "category": "Discussion / Tech News",
                    "location": "Hacker News",
                    "score": self._score(hit),
                    "status": "New",
                    "collection_method": "Public API",
                    "metadata": {
                        "points": hit.get("points"),
                        "comments": hit.get("num_comments"),
                        "created_at": hit.get("created_at"),
                        "object_id": hit.get("objectID"),
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        return results
