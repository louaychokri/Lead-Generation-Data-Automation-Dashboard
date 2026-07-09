import os
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GitHubScraper:
    source_name = "github"

    def __init__(self, keyword: str, max_pages: int = 1, headless: bool = True):
        self.keyword = keyword
        self.max_pages = max_pages
        self.headless = headless

    def close(self):
        pass

    def _session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _score(self, repo: dict) -> int:
        score = 20
        stars = repo.get("stargazers_count", 0) or 0
        forks = repo.get("forks_count", 0) or 0
        if repo.get("description"):
            score += 20
        if repo.get("language"):
            score += 15
        if stars >= 1000:
            score += 30
        elif stars >= 100:
            score += 20
        elif stars >= 10:
            score += 10
        if forks >= 100:
            score += 15
        elif forks >= 10:
            score += 10
        return min(score, 100)

    def scrape(self) -> list[dict]:
        session = self._session()
        token = os.getenv("GITHUB_TOKEN", "").strip()
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "LeadFlow-Pro-Portfolio-Project",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        print("GitHub token loaded:", bool(token))

        results = []
        for page in range(1, self.max_pages + 1):
            response = session.get(
                "https://api.github.com/search/repositories",
                params={"q": self.keyword, "sort": "stars", "order": "desc", "per_page": 20, "page": page},
                headers=headers,
                timeout=60,
            )
            if response.status_code == 403:
                raise RuntimeError(f"GitHub API error 403: {response.text[:300]}")
            response.raise_for_status()
            data = response.json()
            for repo in data.get("items", []):
                owner = repo.get("owner", {}).get("login", "")
                results.append({
                    "title": repo.get("full_name", ""),
                    "name": repo.get("name", ""),
                    "company": owner,
                    "description": repo.get("description") or "",
                    "url": repo.get("html_url", ""),
                    "source": self.source_name,
                    "category": repo.get("language") or "Unknown",
                    "location": "GitHub",
                    "score": self._score(repo),
                    "status": "New",
                    "collection_method": "Official API",
                    "metadata": {
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "open_issues": repo.get("open_issues_count", 0),
                        "updated_at": repo.get("updated_at", ""),
                        "created_at": repo.get("created_at", ""),
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        return results
