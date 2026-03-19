from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

DIRECTORIES = [
    "backend",
    "backend/models",
    "backend/db",
    "backend/utils",
    "backend/data/raw",
    "backend/data/processed",
    "backend/results",
]

INIT_FILES = [
    "backend/models/__init__.py",
    "backend/db/__init__.py",
    "backend/utils/__init__.py",
]

ENV_CONTENT = """DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=smart_city_db
"""


def create_directories() -> None:
    for relative_path in DIRECTORIES:
        (PROJECT_ROOT / relative_path).mkdir(parents=True, exist_ok=True)


def create_init_files() -> None:
    for relative_path in INIT_FILES:
        init_file = PROJECT_ROOT / relative_path
        init_file.touch(exist_ok=True)


def create_env_file() -> None:
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        env_file.write_text(ENV_CONTENT, encoding="utf-8")


def main() -> None:
    create_directories()
    create_init_files()
    create_env_file()
    print("Smart City project structure created successfully.")


if __name__ == "__main__":
    main()
