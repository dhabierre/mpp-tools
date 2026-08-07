import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from builder import build_html_report
from config import build_config
from shared.report import fetch_capital, fetch_capital_trends, fetch_positions, fetch_product_trends, fetch_products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("mpp")


def main() -> None:
    _check_env_file()

    config = build_config()

    logger.info("🔄 Building HTML report...")

    capital = fetch_capital(config.db_path)

    capital_trends = fetch_capital_trends(
        config.db_path,
        config.capital_trends_down_sample_ratio)

    products = fetch_products(config.db_path)

    positions = fetch_positions(config.db_path)

    product_trends = fetch_product_trends(
        config.db_path,
        config.product_trends_cutoff_date,
        config.product_trends_down_sample_max_points)

    html = build_html_report(
        capital,
        capital_trends,
        products,
        positions,
        product_trends,
        config)

    config.report_path.write_text(html, encoding="utf-8")
    logger.info(f"✅ Report written (path: %s)", config.report_path)


def _check_env_file():
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file)
    else:
        logger.error(f"❌ The .env file was not found: %s", env_file.resolve())
        sys.exit(1)


if __name__ == "__main__":
    main()
