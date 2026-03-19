from __future__ import annotations

from pathlib import Path
from typing import Any

import mysql.connector
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"


def _load_env() -> None:
    load_dotenv(ENV_PATH)


def _get_db_config(include_database: bool = True) -> dict[str, Any]:
    _load_env()
    config: dict[str, Any] = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if include_database:
        config["database"] = os.getenv("DB_NAME")

    return config


def get_connection():
    return mysql.connector.connect(**_get_db_config(include_database=True))


def init_db() -> None:
    _load_env()
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise ValueError("DB_NAME is not set in .env")

    server_connection = mysql.connector.connect(**_get_db_config(include_database=False))
    server_cursor = server_connection.cursor()

    try:
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    finally:
        server_cursor.close()
        server_connection.close()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS anomaly_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                model_name VARCHAR(50),
                value FLOAT,
                is_anomaly BOOLEAN,
                reconstruction_error FLOAT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(50),
                anomaly_count INT,
                anomaly_rate FLOAT,
                inference_time_ms FLOAT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()
    finally:
        cursor.close()
        connection.close()


def log_predictions(predictions: dict, model_name: str) -> None:
    timestamps = predictions.get("timestamps", [])
    values = predictions.get("values", [])
    anomalies = predictions.get("anomalies", [])
    reconstruction_errors = predictions.get("reconstruction_errors")

    records = []
    for index, timestamp in enumerate(timestamps):
        records.append(
            (
                timestamp,
                model_name,
                float(values[index]) if index < len(values) else None,
                bool(anomalies[index]) if index < len(anomalies) else False,
                float(reconstruction_errors[index])
                if reconstruction_errors and index < len(reconstruction_errors)
                else None,
            )
        )

    if not records:
        return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.executemany(
            """
            INSERT INTO anomaly_logs
            (timestamp, model_name, value, is_anomaly, reconstruction_error)
            VALUES (%s, %s, %s, %s, %s)
            """,
            records,
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_logs(model_name: str | None = None) -> list[dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if model_name:
            cursor.execute(
                """
                SELECT id, timestamp, model_name, value, is_anomaly,
                       reconstruction_error, created_at
                FROM anomaly_logs
                WHERE model_name = %s
                ORDER BY timestamp DESC
                """,
                (model_name,),
            )
        else:
            cursor.execute(
                """
                SELECT id, timestamp, model_name, value, is_anomaly,
                       reconstruction_error, created_at
                FROM anomaly_logs
                ORDER BY timestamp DESC
                """
            )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_metrics() -> list[dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, model_name, anomaly_count, anomaly_rate,
                   inference_time_ms, recorded_at
            FROM model_metrics
            ORDER BY recorded_at DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def save_metrics(
    model_name: str,
    anomaly_count: int,
    anomaly_rate: float,
    inference_time_ms: float,
) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO model_metrics
            (model_name, anomaly_count, anomaly_rate, inference_time_ms)
            VALUES (%s, %s, %s, %s)
            """,
            (model_name, anomaly_count, anomaly_rate, inference_time_ms),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()
