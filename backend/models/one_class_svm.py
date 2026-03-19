from __future__ import annotations

from pathlib import Path
from time import perf_counter

import joblib
import pandas as pd
from sklearn.svm import OneClassSVM


class OneClassSVMDetector:
    def __init__(self, nu: float = 0.05) -> None:
        self.nu = nu
        self.model = OneClassSVM(nu=nu, kernel="rbf", gamma="scale")

    def _extract_features(self, data: pd.Series, window: int = 24) -> pd.DataFrame:
        series = self._validate_series(data)
        features = pd.DataFrame(index=series.index)
        features["value"] = series
        features["rolling_mean"] = series.rolling(window=window, min_periods=1).mean()
        features["rolling_std"] = (
            series.rolling(window=window, min_periods=1).std().fillna(0.0)
        )
        features["rolling_min"] = series.rolling(window=window, min_periods=1).min()
        features["rolling_max"] = series.rolling(window=window, min_periods=1).max()
        return features

    def fit(self, data: pd.Series) -> None:
        features = self._extract_features(data)
        self.model.fit(features)

    def predict(self, data: pd.Series) -> dict:
        series = self._validate_series(data)
        features = self._extract_features(series)

        start_time = perf_counter()
        raw_predictions = self.model.predict(features)
        inference_time_ms = (perf_counter() - start_time) * 1000

        anomalies = [1 if pred == -1 else 0 for pred in raw_predictions]
        anomaly_count = sum(anomalies)
        total_points = len(anomalies)

        return {
            "timestamps": [str(index) for index in series.index.tolist()],
            "values": series.tolist(),
            "anomalies": anomalies,
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_count / total_points if total_points else 0.0,
            "inference_time_ms": round(inference_time_ms, 3),
        }

    def save(self, path: str | Path) -> None:
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "nu": self.nu,
            },
            model_path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "OneClassSVMDetector":
        payload = joblib.load(path)
        detector = cls(nu=payload["nu"])
        detector.model = payload["model"]
        return detector

    @staticmethod
    def _validate_series(data: pd.Series) -> pd.Series:
        if not isinstance(data, pd.Series):
            raise TypeError("data must be a pandas Series.")

        if data.empty:
            raise ValueError("data must not be empty.")

        series = pd.to_numeric(data, errors="coerce").dropna()
        if series.empty:
            raise ValueError("data must contain at least one numeric value.")

        return series
