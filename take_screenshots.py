# Install first:
# pip install playwright
# python -m playwright install chromium

from pathlib import Path
import subprocess
import sys

from playwright.sync_api import TimeoutError, sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "backend" / "results"
BASE_URL = "http://localhost:5173"


def save_full_page(page, filename: str) -> None:
    path = RESULTS_DIR / filename
    page.screenshot(path=str(path), full_page=True)
    print(f"Screenshot saved: {filename}")


def save_locator_screenshot(locator, filename: str) -> None:
    path = RESULTS_DIR / filename
    locator.screenshot(path=str(path))
    print(f"Screenshot saved: {filename}")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(3000)

        save_full_page(page, "screenshot_dashboard_full.png")

        chart_locator = page.locator("div.recharts-responsive-container").first
        chart_locator.wait_for(state="visible", timeout=10000)
        save_locator_screenshot(chart_locator, "screenshot_chart.png")

        model_targets = [
            ("Isolation Forest", "screenshot_isolation_forest.png"),
            ("LSTM Autoencoder", "screenshot_lstm.png"),
            ("One-Class SVM", "screenshot_ocsvm.png"),
        ]

        for label, filename in model_targets:
            button = page.get_by_role("button", name=label)
            button.click()
            page.wait_for_timeout(2000)
            save_full_page(page, filename)

        bottom_sections = page.locator("section").filter(has_text="Model Comparison").locator("xpath=..").first
        try:
            bottom_sections.wait_for(state="visible", timeout=5000)
            save_locator_screenshot(bottom_sections, "screenshot_comparison.png")
        except TimeoutError:
            comparison_row = page.locator("main .xl\\:grid-cols-\\[1\\.2fr_0\\.8fr\\]").first
            comparison_row.wait_for(state="visible", timeout=5000)
            save_locator_screenshot(comparison_row, "screenshot_comparison.png")

        browser.close()


if __name__ == "__main__":
    main()
