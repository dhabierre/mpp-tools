from datetime import datetime
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import build_config
from history import init_db, save_data
from mpp_client import MPPClient
from shared.models import Position, Product, ProductTrend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("mpp")


def main() -> None:
    _check_env_file()

    config = build_config()
    run_at = datetime.today().isoformat()

    init_db(config)

    client = MPPClient(config)

    client.authenticate()

    capital = _extract_capital(client, run_at, 1)
    capital_trends = _extract_capital_trends(client, run_at, 2)
    products = _extract_products(client, run_at, 3)
    positions = _extract_positions(client, run_at, 4)
    product_trends = _extract_product_trends(client, positions, run_at, 5)
    invest_orders = _extract_invest_orders(client, products, run_at, 6)

    save_data(capital, capital_trends, products, positions, product_trends, invest_orders, config)

    logger.info(f"🏁 Data stored (db: %s)", config.db_path)


def _extract_capital(client: MPPClient, run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Capital' data...", index)
    data = client.fetch_capital(run_at)
    logger.info(f"✅ [%d /6] Data 'Capital' extracted.", index)
    return data


def _extract_capital_trends(client: MPPClient, run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Capital Trends' data...", index)
    data = client.fetch_capital_trends(run_at)
    logger.info(f"✅ [%d /6] Data 'Capital Trends' extracted ({len(data)}).", index)
    return data


def _extract_products(client: MPPClient, run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Products' data...", index)
    data = client.fetch_products(run_at)
    logger.info(f"✅ [%d /6] Data 'Products' extracted ({len(data)}).", index)
    return data


def _extract_positions(client: MPPClient, run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Positions' data...", index)
    data = client.fetch_positions(run_at)
    logger.info(f"✅ [%d /6] Data 'Positions' extracted ({len(data)}).", index)
    return data


def _extract_product_trends(client: MPPClient, positions: dict[str, Position], run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Product Trends' data...", index)
    data: list[ProductTrend] = []
    for p in positions.values():
        trends = client.fetch_product_trends(p.guid, p.slug, p.name, run_at)
        data.extend(trends)
    logger.info(f"✅ [%d /6] Data 'Product Trends' extracted ({len(data)}).", index)
    return data


def _extract_invest_orders(client: MPPClient, products: dict[str, Product], run_at: str, index: int):
    logger.info(f"🔄 [%d /6] Extracting 'Invest Orders' data...", index)
    data = client.fetch_invest_orders(run_at, products)
    logger.info(f"✅ [%d /6] Data 'Invest Orders' extracted ({len(data)}).", index)
    return data


def _check_env_file():
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file)
    else:
        logger.error(f"❌ The .env file was not found: %s", env_file.resolve())
        sys.exit(1)


if __name__ == "__main__":
    main()
