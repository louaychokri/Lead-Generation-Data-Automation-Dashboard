from datetime import datetime
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


def export_csv(items: list[dict]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EXPORT_DIR / f"leadflow_export_{timestamp}.csv"
    df = pd.DataFrame(items)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
