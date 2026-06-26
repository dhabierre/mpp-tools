from collections import defaultdict
from datetime import date
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from sampling import reduce_points_by_ratio, reduce_points_to_limit
from shared.models import Capital, CapitalTrend, InvestOrder, Position, Product, ProductTrend

def fetch_capital(
    config: Config
) -> Capital:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT *
        FROM capital;
        """
    ).fetchone()
    conn.close()
    return Capital.from_row(dict(row))


def fetch_capital_trends(
    config: Config
) -> list[CapitalTrend]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT *
        FROM capital_trends
        ORDER BY date ASC;
        """
    ).fetchall()
    conn.close()
    capital_trends = [CapitalTrend.from_row(dict(row)) for row in rows]
    return reduce_points_by_ratio(
        capital_trends,
        config.capital_trends_down_sample_ratio)


def fetch_products(
    config: Config
) -> dict[str, Product]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT *
        FROM products;
        """
    ).fetchall()
    conn.close()
    return {row["guid"]: Product.from_row(dict(row)) for row in rows}


def fetch_positions(
    config: Config
) -> list[Position]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT *
        FROM positions
        ORDER BY (amount - invested_amount) DESC;
        """
    ).fetchall()
    conn.close()
    return [Position.from_row(dict(row)) for row in rows]


def fetch_product_trends(
    config: Config
) -> list[ProductTrend]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"""
        SELECT *
        FROM product_trends
        WHERE date >= '{config.product_trends_cutoff_date}'
        ORDER BY date ASC;
        """
    ).fetchall()
    conn.close()

    product_trends = defaultdict(list)
    for row in rows:
        trend = ProductTrend.from_row(dict(row))
        product_trends[trend.guid].append(trend)
    
    for guid in product_trends:
        product_trends[guid] = reduce_points_to_limit(
            product_trends[guid],
            config.product_trends_down_sample_max_points)

    invest_orders = fetch_invest_orders(config)

    # SELECT type, sub_type, row_type, COUNT(*) FROM invest_orders GROUP BY type, sub_type, row_type ORDER BY COUNT(*) DESC
    # 
    # type    |sub_type          |row_type|count(*)|
    # --------+------------------+--------+--------+
    # buy     |monthly-investment|buy     |     496|
    # buy     |free-investment   |buy     |      31|
    # exchange|exchange          |buy     |      19|
    # buy     |initial-investment|buy     |      10|
    # exchange|exchange          |sell    |      10|
    # exchange|corporate-action  |buy     |       2|
    # exchange|corporate-action  |sell    |       1|

    for guid in product_trends:
        _enrich_with(product_trends, invest_orders, guid, "initial-investment", "buy", "INITIAL_INVESTMENT_BUY_ORDER")  # must be first one
        _enrich_with(product_trends, invest_orders, guid, "monthly-investment", "buy", "MONTHLY_INVESTMENT_BUY_ORDER")
        _enrich_with(product_trends, invest_orders, guid, "free-investment", "buy", "FREE_INVESTMENT_BUY_ORDER")
        _enrich_with(product_trends, invest_orders, guid, "exchange", "buy", "EXCHANGE_BUY_ORDER")
        _enrich_with(product_trends, invest_orders, guid, "exchange", "sell", "EXCHANGE_SELL_ORDER")

    return product_trends


def _enrich_with(
    product_trends: dict[str, list[ProductTrend]],
    invest_orders: list[InvestOrder],
    guid: str,
    sub_type: str,
    row_type: str,
    tag: str
) -> None:
    product_orders = sorted(
        [o for o in invest_orders if o.row_guid == guid],
            key=lambda o: o.processed_at
        )
    scoped_orders = [o for o in product_orders if o.sub_type == sub_type and o.row_type == row_type]
    if not scoped_orders:
        if tag == "INITIAL_INVESTMENT_BUY_ORDER":
            scoped_orders = [o for o in product_orders if o.row_type == "buy"]
            scoped_orders = [scoped_orders[0]]
    for o in scoped_orders:
        exists = next((i for i in product_trends[guid] if i.date == o.processed_at), None)
        if exists:
            if exists.tag is None:
                exists.tag = tag
            continue
        closest = min(
            product_trends[guid],
            key=lambda x: abs(
                (date.fromisoformat(x.date) - date.fromisoformat(o.processed_at)).total_seconds()
            )
        )
        product_trends[guid].append(
            ProductTrend(
                guid=guid,
                slug=closest.slug,
                name=closest.name,
                amount=closest.amount,
                date=o.processed_at,
                run_at=None,
                tag=tag
            ))
    product_trends[guid].sort(key=lambda x: x.date)


def fetch_invest_orders(
    config: Config
) -> list[InvestOrder]:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT *
        FROM invest_orders
    """).fetchall()
    conn.close()
    return [InvestOrder.from_row(dict(r)) for r in rows]
