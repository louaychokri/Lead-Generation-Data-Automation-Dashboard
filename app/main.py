from dotenv import load_dotenv
load_dotenv()

import argparse
from app.scrapers.github_scraper import GitHubScraper
from app.scrapers.hackernews_api_scraper import HackerNewsAPIScraper
from app.scrapers.remoteok_api_scraper import RemoteOKAPIScraper
from app.scrapers.stackexchange_api_scraper import StackExchangeAPIScraper
from app.database.db import init_db, save_items, count_items, fetch_all_items
from app.exporters.csv_exporter import export_csv
from app.exporters.excel_exporter import export_excel
from app.utils.logger import get_logger

logger = get_logger("leadflow.main")

SCRAPERS = {
    "github": GitHubScraper,
    "hackernews": HackerNewsAPIScraper,
    "remoteok": RemoteOKAPIScraper,
    "stackexchange": StackExchangeAPIScraper,
}


def ask_choice(prompt: str, choices: list[str], default: str) -> str:
    choices_text = " / ".join(choices)
    while True:
        value = input(f"{prompt} ({choices_text}) [default: {default}]: ").strip().lower()
        if not value:
            return default
        if value in choices:
            return value
        print(f"Invalid choice. Please choose one of: {choices_text}")


def ask_text(prompt: str, default: str) -> str:
    value = input(f"{prompt} [default: {default}]: ").strip()
    return value or default


def ask_int(prompt: str, default: int, min_value: int = 1, max_value: int = 10) -> int:
    while True:
        value = input(f"{prompt} [default: {default}]: ").strip()
        if not value:
            return default
        try:
            number = int(value)
            if min_value <= number <= max_value:
                return number
            print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Please enter a valid number.")


def interactive_mode() -> tuple[str, str, int]:
    print("\n==============================")
    print("LeadFlow Pro Interactive Mode")
    print("==============================\n")
    print("Available sources:")
    print("1. github        - GitHub repositories API")
    print("2. hackernews    - Hacker News API")
    print("3. remoteok      - Remote jobs JSON feed")
    print("4. stackexchange - StackOverflow API")
    print("5. all           - Run all sources\n")

    source = ask_choice("Choose source", ["github", "hackernews", "remoteok", "stackexchange", "all"], "github")
    keyword = ask_text("Enter search keyword", "python automation")
    max_pages = ask_int("Enter max pages", 1, 1, 10)
    return source, keyword, max_pages


def run_source(source_name: str, keyword: str, max_pages: int) -> int:
    scraper_class = SCRAPERS[source_name]
    scraper = scraper_class(keyword=keyword, max_pages=max_pages, headless=True)
    try:
        logger.info(f"Starting scraper: {source_name} | keyword={keyword}")
        items = scraper.scrape()
        saved_count = save_items(items)
        logger.info(f"{source_name} completed. Saved {saved_count} new items.")
        print(f"✅ {source_name}: saved {saved_count} new items")
        return saved_count
    except Exception as exc:
        logger.error(f"Source {source_name} stopped: {exc}")
        print(f"[SAFE STOP] {source_name}: {exc}")
        return 0
    finally:
        if hasattr(scraper, "close"):
            scraper.close()


def main():
    parser = argparse.ArgumentParser(description="LeadFlow Pro - API-first web intelligence automation tool")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("--source", choices=["all", "github", "hackernews", "remoteok", "stackexchange"], default=None)
    parser.add_argument("--keyword", default=None)
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()

    if args.interactive or args.source is None or args.keyword is None or args.max_pages is None:
        source, keyword, max_pages = interactive_mode()
    else:
        source, keyword, max_pages = args.source, args.keyword, args.max_pages

    init_db()
    sources = list(SCRAPERS.keys()) if source == "all" else [source]
    total_saved = 0

    for selected_source in sources:
        total_saved += run_source(selected_source, keyword, max_pages)

    all_items = fetch_all_items()
    excel_path = export_excel(all_items)
    csv_path = export_csv(all_items)

    print("\n==============================")
    print("LeadFlow Pro Finished")
    print("==============================")
    print(f"Excel exported: {excel_path}")
    print(f"CSV exported: {csv_path}")
    print(f"New saved items: {total_saved}")
    print(f"Total database items: {count_items()}")


if __name__ == "__main__":
    main()
