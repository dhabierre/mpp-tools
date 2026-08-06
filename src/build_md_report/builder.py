"""Build a Markdown version of the MPP portfolio report.

The Markdown report deliberately replaces the HTML charts with monthly snapshots.
This keeps the history readable by NotebookLM while preserving the main signals of
the graphical report.
"""

from __future__ import annotations

import sys
from calendar import monthrange
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from shared.models import Capital, CapitalTrend, Position, Product, ProductTrend


PERFORMANCE_PERIODS = (("1M", 1), ("3M", 3), ("6M", 6), ("1Y", 12))
PERFORMANCE_PERIOD_LABELS = {
    "1M": "1 month",
    "3M": "3 months",
    "6M": "6 months",
    "1Y": "1 year",
}


def build_md_report(
    capital: Capital | None,
    capital_trends: list[CapitalTrend],
    products: dict[str, Product],
    positions: list[Position],
    product_trends: dict[str, list[ProductTrend]],
    config: Config,
) -> str:
    """Return a NotebookLM-friendly Markdown report."""
    generated_at = datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M %Z")
    sections = [
        "# MPP Report",
        f"Generated at: {generated_at}",
        "",
        "## Portfolio Summary",
        _render_summary(capital),
        "",
        "## 📈 Capital Trends",
        _render_capital_trends(capital_trends),
        "",
        "## 💲 Positions",
        _render_positions(capital, positions, products, config),
        "",
        "## 📈 Product Trends",
        _render_product_trends(product_trends, positions),
        "",
        "---",
        "Source: [MPP Tools](https://github.com/dhabierre/mpp-tools)",
    ]
    return "\n".join(sections).strip() + "\n"


def _render_summary(capital: Capital | None) -> str:
    if capital is None:
        return "No current capital valuation is available."
    return _markdown_table(
        ["Invested", "Capital", "Gain", "Performance", "Annualized performance", "Last valuation"],
        [[
            _eur(capital.invested_amount),
            _eur(capital.amount),
            _signed_eur(capital.gain),
            _percent(capital.performance),
            _percent(capital.annualized_performance),
            capital.last_valuated_at or "—",
        ]],
    )


def _render_capital_trends(trends: list[CapitalTrend]) -> str:
    monthly = _latest_by_month(trends)
    if not monthly:
        return "No capital history is available."
    rows = []
    previous_amount: float | None = None
    for month, trend in monthly:
        change = trend.amount - previous_amount if previous_amount is not None else None
        change_percent = (
            change / previous_amount * 100
            if change is not None and previous_amount
            else None
        )
        rows.append([
            month,
            _eur(trend.invested_amount),
            _eur(trend.amount),
            _signed_eur(change) if change is not None else "—",
            _percent(change_percent),
            _signed_eur(trend.gain),
            _percent(trend.performance),
        ])
        previous_amount = trend.amount
    return _markdown_table(
        ["Month", "Invested", "Capital", "Change", "Change %", "Gain", "Performance"],
        rows,
    )


def _render_positions(
    capital: Capital | None,
    positions: list[Position],
    products: dict[str, Product],
    config: Config,
) -> str:
    total_amount = capital.amount if capital else 0
    rows = []
    for position in sorted(positions, key=lambda item: item.amount, reverse=True):
        product = products.get(position.guid)
        gain = position.amount - position.invested_amount
        weight = position.amount / total_amount * 100 if total_amount else 0
        resources = _resources(position.guid, product.isin if product else None, config)
        rows.append([
            position.name,
            _percent(position.performance),
            _eur(position.amount),
            _eur(position.invested_amount),
            _signed_eur(gain),
            _percent(weight),
            str(int(product.risk)) if product and product.risk else "—",
            _percent(product.fee_rate, signed=False) if product and product.fee_rate else "—",
            resources,
        ])
    if capital:
        rows.append([
            "**Total**",
            _eur(capital.invested_amount),
            _eur(capital.amount),
            _percent(capital.performance),
            _signed_eur(capital.gain),
            "—", "—", "—", "—",
        ])
    return _markdown_table(
        ["Position", "Invested", "Capital", "Performance", "Gain", "Weight", "Risk", "Fee", "Resources"],
        rows,
    ) if rows else "No positions are available."


def _render_product_trends(
    product_trends: dict[str, list[ProductTrend]],
    positions: list[Position],
) -> str:
    position_by_guid = {position.guid: position for position in positions}
    blocks: list[str] = []
    for guid, trends in sorted(product_trends.items(), key=lambda item: item[1][0].name if item[1] else item[0]):
        if not trends:
            continue
        position = position_by_guid.get(guid)
        latest = max(trends, key=lambda trend: trend.date)
        performance = _percent(position.performance) if position else "—"
        period_performances = _calculate_period_performances(trends)
        period_bullets = _render_period_performances(period_performances)
        monthly = _latest_by_month(trends)
        rows = []
        previous_amount: float | None = None
        for month, trend in monthly:
            change = trend.amount - previous_amount if previous_amount is not None else None
            change_percent = (
                change / previous_amount * 100
                if change is not None and previous_amount
                else None
            )
            rows.append([
                month,
                _eur(trend.amount),
                _signed_eur(change) if change is not None else "—",
                _percent(change_percent),
            ])
            previous_amount = trend.amount
        blocks.extend([
            f"### 📌 {latest.name}",
            f"Current performance: {performance}",
            "",
            "Period performance:",
            period_bullets,
            "",
            _markdown_table(["Month", "Current", "Change", "Change %"], rows),
            "",
        ])
    return "\n".join(blocks).rstrip() if blocks else "No product history is available."


def _latest_by_month(trends: list[CapitalTrend] | list[ProductTrend]) -> list[tuple[str, CapitalTrend | ProductTrend]]:
    """Keep the last available valuation for each calendar month."""
    by_month: dict[str, CapitalTrend | ProductTrend] = {}
    for trend in sorted(trends, key=lambda item: item.date):
        by_month[trend.date[:7]] = trend
    return list(by_month.items())


def _calculate_period_performances(product_trends: list[ProductTrend]) -> list[tuple[str, float | None]]:
    dated_trends = sorted(((date.fromisoformat(t.date), t.amount) for t in product_trends), key=lambda item: item[0])
    if not dated_trends:
        return [(label, None) for label, _ in PERFORMANCE_PERIODS]
    current_date, current_amount = dated_trends[-1]
    performances = []
    for label, months in PERFORMANCE_PERIODS:
        reference_date = _subtract_months(current_date, months)
        reference = next((item for item in reversed(dated_trends) if item[0] <= reference_date), None)
        performances.append((label, (current_amount / reference[1] - 1) * 100 if reference and reference[1] else None))
    return performances


def _render_period_performances(performances: list[tuple[str, float | None]]) -> str:
    return "\n".join(
        f"- {PERFORMANCE_PERIOD_LABELS[label]}: {_percent(value)}"
        for label, value in performances
    )


def _subtract_months(value: date, months: int) -> date:
    year_offset, month_index = divmod(value.month - months - 1, 12)
    year, month = value.year + year_offset, month_index + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "No data is available."
    header = "| " + " | ".join(_escape_cell(cell) for cell in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(_escape_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _eur(value: float | None) -> str:
    return f"{(value or 0):,.2f} €"


def _signed_eur(value: float | None) -> str:
    return f"{(value or 0):+,.2f} €"


def _percent(value: float | None, signed: bool = True) -> str:
    if value is None:
        return "—"
    return f"{value:+.2f} %" if signed else f"{value:.2f} %"


def _resources(guid: str, isin: str | None, config: Config) -> str:
    mpp = f"[MPP](https://app.monpetitplacement.fr/comptes/{config.user_investment_account_id}/dashboard/produits-investis/{guid}/compartiments/default)"
    ft = f"[FT](https://markets.ft.com/data/funds/tearsheet/summary?s={isin}:EUR)" if isin else ""
    return " · ".join(item for item in (mpp, ft) if item)
