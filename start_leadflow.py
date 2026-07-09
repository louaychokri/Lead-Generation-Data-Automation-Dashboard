import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = PROJECT_ROOT / "run_dashboard.py"


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


def run_scraper(source: str, keyword: str, max_pages: int) -> None:
    print("\n==============================")
    print("Running LeadFlow scraper")
    print("==============================\n")

    command = [
        sys.executable,
        "-m",
        "app.main",
        "--source",
        source,
        "--keyword",
        keyword,
        "--max-pages",
        str(max_pages),
    ]

    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("\nScraper stopped with an error. Fix the error above, then run this launcher again.")
        sys.exit(result.returncode)

    print("\nScraper finished successfully.")


def open_dashboard() -> None:
    print("\n==============================")
    print("Opening Streamlit dashboard")
    print("==============================\n")

    if not DASHBOARD_FILE.exists():
        print(f"Dashboard file not found: {DASHBOARD_FILE}")
        sys.exit(1)

    command = [sys.executable, "-m", "streamlit", "run", str(DASHBOARD_FILE)]
    subprocess.Popen(command, cwd=PROJECT_ROOT)


def main():
    print("\n==============================")
    print("LeadFlow Launcher")
    print("==============================\n")
    print("Available sources:")
    print("1. github        - GitHub repositories API")
    print("2. hackernews    - Hacker News API")
    print("3. remoteok      - Remote jobs JSON feed")
    print("4. stackexchange - StackOverflow API")
    print("5. all           - Run all sources\n")

    source = ask_choice("Choose source", ["github", "hackernews", "remoteok", "stackexchange", "all"], "github")
    keyword = ask_text("Enter search keyword", "python")
    max_pages = ask_int("Enter max pages", 1, 1, 10)

    run_scraper(source, keyword, max_pages)
    open_dashboard()

    print("\nDone. The dashboard should open in your browser.")
    print("If it does not open automatically, copy the Local URL from the terminal.")


if __name__ == "__main__":
    main()
