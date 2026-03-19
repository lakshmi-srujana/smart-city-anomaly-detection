import os

import mysql.connector
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        if connection.is_connected():
            print("MySQL connection successful.")
            print(f"Connected to database: {os.getenv('DB_NAME')}")
            print(f"MySQL server version: {connection.get_server_info()}")

        connection.close()

    except mysql.connector.Error as error:
        print(f"MySQL connection failed: {error}")


if __name__ == "__main__":
    main()
