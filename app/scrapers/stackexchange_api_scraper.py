from datetime import datetime, timezone
import requests


class StackExchangeAPIScraper:
    source_name = "stackexchange"

    def __init__(self, keyword: str, max_pages: int = 1, headless: bool = True):
        self.keyword = keyword
        self.max_pages = max_pages
        self.headless = headless

    def close(self):
        pass

    def _score(self, question: dict) -> int:
        score = 20
        if question.get("is_answered"):
            score += 20
        views = question.get("view_count") or 0
        answers = question.get("answer_count") or 0
        q_score = question.get("score") or 0
        if views >= 10000:
            score += 25
        elif views >= 1000:
            score += 15
        if answers >= 5:
            score += 20
        elif answers >= 1:
            score += 10
        if q_score >= 50:
            score += 20
        elif q_score >= 5:
            score += 10
        return min(score, 100)

    def scrape(self) -> list[dict]:
        results = []
        for page in range(1, self.max_pages + 1):
            response = requests.get(
                "https://api.stackexchange.com/2.3/search/advanced",
                params={
                    "order": "desc",
                    "sort": "relevance",
                    "q": self.keyword,
                    "site": "stackoverflow",
                    "pagesize": 20,
                    "page": page,
                },
                headers={"User-Agent": "LeadFlow-Pro-Portfolio-Project"},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            for q in data.get("items", []):
                title = q.get("title", "Untitled")
                owner = q.get("owner", {}).get("display_name", "")
                results.append({
                    "title": title,
                    "name": title,
                    "company": owner,
                    "description": f"StackOverflow question. Views: {q.get('view_count', 0)}. Answers: {q.get('answer_count', 0)}. Score: {q.get('score', 0)}.",
                    "url": q.get("link", ""),
                    "source": self.source_name,
                    "category": ", ".join(q.get("tags", [])),
                    "location": "Stack Overflow",
                    "score": self._score(q),
                    "status": "New",
                    "collection_method": "Official API",
                    "metadata": {
                        "views": q.get("view_count"),
                        "answers": q.get("answer_count"),
                        "question_score": q.get("score"),
                        "is_answered": q.get("is_answered"),
                        "question_id": q.get("question_id"),
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        return results
