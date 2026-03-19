from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models import (
    IsolationForestDetector,
    LSTMAutoencoder,
    OneClassSVMDetector,
)
from backend.utils import load_clean_data

RESULTS_DIR = PROJECT_ROOT / "backend" / "results"
PLOT_PATH = RESULTS_DIR / "model_comparison.png"


def evaluate_models() -> pd.DataFrame:
    df = load_clean_data()
    series = df["Global_active_power"]

    models = [
      ("Isolation Forest", IsolationForestDetector(contamination=0.05)),
      ("LSTM Autoencoder", LSTMAutoencoder(seq_length=24, threshold_percentile=95)),
      ("One-Class SVM", OneClassSVMDetector(nu=0.05)),
    ]

    rows = []
    for model_name, model in models:
        if isinstance(model, LSTMAutoencoder):
            model.fit(series, epochs=20, batch_size=32)
        else:
            model.fit(series)

        predictions = model.predict(series)
        rows.append(
            {
                "Model": model_name,
                "Anomalies_Detected": predictions["anomaly_count"],
                "Anomaly_Rate_%": round(predictions["anomaly_rate"] * 100, 2),
                "Inference_Time_ms": round(predictions["inference_time_ms"], 3),
            }
        )

    comparison_df = pd.DataFrame(rows)
    print(comparison_df.to_string(index=False))

    _save_comparison_plot(comparison_df)
    return comparison_df


def _save_comparison_plot(comparison_df: pd.DataFrame) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    labels = comparison_df["Model"].tolist()
    anomaly_counts = comparison_df["Anomalies_Detected"].to_numpy(dtype=float)
    anomaly_rates = comparison_df["Anomaly_Rate_%"].to_numpy(dtype=float)
    inference_times = comparison_df["Inference_Time_ms"].to_numpy(dtype=float)

    count_scale = anomaly_counts / max(anomaly_counts.max(), 1) * 100
    rate_scale = anomaly_rates
    time_scale = inference_times / max(inference_times.max(), 1) * 100

    y = np.arange(len(labels))
    bar_height = 0.22

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(
        y - bar_height,
        count_scale,
        height=bar_height,
        color="#4f46e5",
        label="Anomalies Detected (normalized)",
    )
    ax.barh(
        y,
        rate_scale,
        height=bar_height,
        color="#f59e0b",
        label="Anomaly Rate (%)",
    )
    ax.barh(
        y + bar_height,
        time_scale,
        height=bar_height,
        color="#10b981",
        label="Inference Time (normalized)",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Comparison Scale")
    ax.set_title("Model Comparison")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.legend(loc="lower right")

    for idx, value in enumerate(anomaly_rates):
        ax.text(rate_scale[idx] + 1, y[idx], f"{value:.2f}%", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    evaluate_models()
