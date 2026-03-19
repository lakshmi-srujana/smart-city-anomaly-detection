from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_CANDIDATES = [
    PROJECT_ROOT / "backend" / "data" / "raw" / "household_power_consumption.txt",
    PROJECT_ROOT / "data" / "raw" / "household_power_consumption.txt",
]
OUTPUT_PATH = PROJECT_ROOT / "backend" / "data" / "processed" / "power_clean.csv"


def _resolve_raw_data_path() -> Path:
    for path in RAW_DATA_CANDIDATES:
        if path.exists():
            return path

    expected_paths = "\n".join(str(path) for path in RAW_DATA_CANDIDATES)
    raise FileNotFoundError(
        "Could not find household_power_consumption.txt in any expected location:\n"
        f"{expected_paths}"
    )


def load_clean_data() -> pd.DataFrame:
    raw_data_path = _resolve_raw_data_path()

    df = pd.read_csv(raw_data_path, sep=";", na_values="?")
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )
    df = df.dropna(subset=["datetime"]).set_index("datetime")
    df = df.drop(columns=["Date", "Time"])

    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.sort_index().ffill().resample("h").mean()

    scaler = MinMaxScaler()
    df["Global_active_power"] = scaler.fit_transform(
        df[["Global_active_power"]]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH)

    return df
