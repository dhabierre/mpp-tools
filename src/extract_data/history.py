from dataclasses import asdict
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from shared.models import Capital, CapitalTrend, InvestOrder, Position, Product, ProductTrend


def init_db(
    config: Config
) -> None:
    conn = sqlite3.connect(config.db_path)
    conn.execute("PRAGMA journal_mode=WAL;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS capital (
            amount REAL NOT NULL,
            invested_amount REAL NOT NULL,
            performance REAL NOT NULL,
            annualized_performance REAL NOT NULL,
            gain REAL NOT NULL,
            date TEXT NOT NULL,
            run_at TEXT NOT NULL
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS capital_trends (
            date TEXT NOT NULL,
            performance REAL NOT NULL,
            gain REAL NOT NULL,
            amount REAL NOT NULL,
            invested_amount REAL NOT NULL,
            run_at TEXT NOT NULL,
            UNIQUE(date)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            guid TEXT NOT NULL,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            isin TEXT, -- can ne NULL
            risk REAL NOT NULL,
            fee_rate REAL NOT NULL,
            dic_path TEXT NOT NULL,
            run_at TEXT NOT NULL,
            UNIQUE(guid)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            guid TEXT NOT NULL,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            invested_amount REAL NOT NULL,
            performance REAL NOT NULL,
            date TEXT NOT NULL,
            run_at TEXT NOT NULL,
            UNIQUE(guid, date)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS product_trends (
            guid TEXT NOT NULL,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            run_at TEXT NOT NULL,
            UNIQUE(guid, date)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS invest_orders (
            reference TEXT NOT NULL,
            type TEXT NOT NULL,
            sub_type TEXT NOT NULL,
            amount REAL NOT NULL,
            processed_at TEXT NOT NULL,
            valuated_at TEXT NOT NULL,
            row_id TEXT NOT NULL,
            row_type TEXT NOT NULL,
            row_amount REAL NOT NULL,
            row_guid TEXT NOT NULL,
            row_slug TEXT NOT NULL,
            row_name TEXT NOT NULL,
            run_at TEXT NOT NULL,
            UNIQUE(reference, row_id)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS _cursors (
            id TEXT NOT NULL,
            guid TEXT NOT NULL,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            page INTEGER NOT NULL,
            size INTEGER NOT NULL,
            update_at TEXT NOT NULL,
            UNIQUE(id, guid)
        );
    """)

    conn.commit()
    conn.close()


def save_data(
    capital: Capital,
    capital_trends: list[CapitalTrend],
    products: dict[str, Product],
    positions: dict[str, Position],
    product_trends: list[ProductTrend],
    invest_orders: list[InvestOrder],
    config: Config
) -> None:

    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM capital;")

    cursor.execute("""
        INSERT INTO capital
        (amount, invested_amount, performance, annualized_performance, gain, date, run_at)
        VALUES (:amount, :invested_amount, :performance, :annualized_performance, :gain, :date, :run_at)
        ;
    """, capital.to_db_row())

    cursor.execute("DELETE FROM capital_trends;")

    cursor.executemany("""
        INSERT INTO capital_trends
        (date, performance, gain, amount, invested_amount, run_at)
        VALUES (:date, :performance, :gain, :amount, :invested_amount, :run_at)
        ON CONFLICT(date) DO NOTHING
        ;
    """, [asdict(i) for i in capital_trends])

    cursor.execute("DELETE FROM products;")

    cursor.executemany("""
        INSERT INTO products
        (guid, slug, name, isin, risk, fee_rate, dic_path, run_at)
        VALUES (:guid, :slug, :name, :isin, :risk, :fee_rate, :dic_path, :run_at)
        ;
    """, [product.to_db_row() for product in products.values()])

    cursor.execute("DELETE FROM positions;")

    cursor.executemany("""
        INSERT INTO positions
        (guid, slug, name, amount, invested_amount, performance, date, run_at)
        VALUES (:guid, :slug, :name, :amount, :invested_amount, :performance, :date, :run_at)
        ;
    """, [position.to_db_row() for position in positions.values()])

    cursor.executemany("""
        INSERT INTO product_trends
        (guid, slug, name, amount, date, run_at)
        VALUES (:guid, :slug, :name, :amount, :date, :run_at)
        ON CONFLICT(guid, date) DO NOTHING
        ;
    """, [asdict(i) for i in product_trends])

    cursor.executemany("""
        INSERT INTO invest_orders
        (reference, type, sub_type, amount, processed_at, valuated_at, row_id, row_type, row_amount, row_guid, row_slug, row_name, run_at)
        VALUES (:reference, :type, :sub_type, :amount, :processed_at, :valuated_at, :row_id, :row_type, :row_amount, :row_guid, :row_slug, :row_name, :run_at)
        ON CONFLICT(reference, row_id) DO NOTHING
        ;
    """, [asdict(i) for i in invest_orders])

    conn.commit()
    conn.close()
