from datetime import datetime, timezone
import requests


class RemoteOKAPIScraper:
    source_name = "remoteok"

    def __init__(self, keyword: str, max_pages: int = 1, headless: bool = True):
        self.keyword = keyword.lower()
        self.max_pages = max_pages
        self.headless = headless

    def close(self):
        pass

    def _score(self, job: dict) -> int:
        score = 20
        if job.get("company"):
            score += 20
        if job.get("position"):
            score += 20
        if job.get("url") or job.get("apply_url"):
            score += 15
        if job.get("tags"):
            score += 15
        if job.get("salary_min") or job.get("salary_max"):
            score += 20
        return min(score, 100)

    def scrape(self) -> list[dict]:
        response = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "LeadFlow-Pro-Portfolio-Project", "Accept": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        results = []
        limit = self.max_pages * 20

        for job in data:
            if not isinstance(job, dict) or not job.get("position"):
                continue
            position = job.get("position", "") or ""
            company = job.get("company", "") or ""
            tags = job.get("tags", []) or []
            tags_text = " ".join(tags)
            searchable = f"{position} {company} {tags_text}".lower()
            if self.keyword and self.keyword not in searchable:
                continue
            url = job.get("url") or job.get("apply_url") or f"https://remoteok.com/remote-jobs/{job.get('id', '')}"
            results.append({
                "title": position,
                "name": position,
                "company": company,
                "description": job.get("description", "") or "",
                "url": url,
                "source": self.source_name,
                "category": tags_text,
                "location": job.get("location", "Remote") or "Remote",
                "score": self._score(job),
                "status": "New",
                "collection_method": "JSON Feed",
                "metadata": {
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "date": job.get("date"),
                    "job_id": job.get("id"),
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            if len(results) >= limit:
                break
        return results
