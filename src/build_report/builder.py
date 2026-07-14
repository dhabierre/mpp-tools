import sys
from calendar import monthrange
from datetime import date, datetime
from zoneinfo import ZoneInfo
from html import escape
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from shared.models import Capital, CapitalTrend, Position, Product, ProductTrend

RECENT_TREND_WINDOW = 30  # calculate the trend slope
PERFORMANCE_PERIODS = (("1M", 1), ("3M", 3), ("6M", 6), ("1Y", 12))

COLOR_PERFORMANCE = "#4F82F0"
COLOR_PERFORMANCE_ZERO = "#152444"

COLOR_GAIN = "#be3f98"
COLOR_GAIN_ZERO = "#50143F"

COLOR_CAPITAL = COLOR_PERFORMANCE
COLOR_INVESTED = COLOR_GAIN

COLOR_GREEN = "#3fb950"
COLOR_BLUE = "#0000ff"
COLOR_CYAN = "#00ffff"
COLOR_RED = "#fd483f"
COLOR_YELLOW = "#ffe949"


def build_html_report(
    capital: Capital,
    capital_trends: list[CapitalTrend],
    products: dict[str, Product],
    positions: list[Position],
    product_trends: dict[str, list[ProductTrend]],
    config: Config
) -> str:
    return _render_html(
        capital,
        capital_trends,
        products,
        positions,
        product_trends,
        config)


def _render_html(
    capital: Capital,
    capital_trends: list[CapitalTrend],
    products: dict[str, Product],
    positions: list[Position],
    product_trends: dict[str, list[ProductTrend]],
    config: Config
) -> str:
    generated_at = datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M")

    capital_trends_performance_html = _render_capital_trends_by_performance(capital_trends)
    capital_trends_amounts_html = _render_capital_trends_by_amounts(capital_trends)
    positions_html = _render_positions(capital, positions, products, config)
    product_trends_html = _render_product_trends(product_trends, positions)

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>MPP Report</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link href="styles.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
</head>
<body>
  <h1>
    <img src="favicon.svg" class="mpp-logo" />
    MPP Report
  </h1>
  <div class="card">
    <h2>📈 Capital Trends</h2>
    <div class="trends-grid-ct">
      {capital_trends_performance_html}
      {capital_trends_amounts_html}
    </div>
  </div>
  <div class="card">
    <h2>💲 Positions</h2>
    {positions_html}
  </div>
  <div class="card">
    <h2>📈 Product Trends</h2>
    <div class="trends-grid-pt">
      {product_trends_html}
    </div>
  </div>
  <div class="card footer">
    <span class="muted">Generated at {generated_at}</span>
    <div class="footer-links">
        <a href="https://github.com/dhabierre/mpp-tools" target="_blank" rel="noopener noreferrer">
        <img src="github.png" alt="GitHub" title="GitHub Project" width="50">
        </a>
        <a href="https://www.monpetitplacement.fr/" target="_blank" rel="noopener noreferrer">
        <img src="favicon.svg" title="Mon Petit Placement" width="30" />
        </a>
    </div>
  </div>
</body>
</html>
"""


def _render_capital_trends_by_performance(
    capital_trends: list[CapitalTrend]
) -> str:
    labels = [t.date for t in capital_trends]
    values = {
        "performance": [t.performance for t in capital_trends],
        "gain": [t.gain for t in capital_trends]
    }
    values["max_performance"] = max(values["performance"], default=0)
    values["max_gain"] = max(values["gain"], default=0)
    canvas_id = "capital_trends_performance_chart"
    return f"""
<div class="chart-container-ct">
    <h3>
        Performance & Gain
    </h3>
    <canvas id="{canvas_id}" />
    <script>
        const labels_pg = {json.dumps(labels)};
        const data_pg = {json.dumps(values)};
        const minPerformanceValue = Math.round(Math.min(...data_pg.performance), 0);
        const maxPerformanceValue = Math.round(Math.max(...data_pg.performance), 0) + 1;
        const minGainValue = Math.round(Math.min(...data_pg.gain), 0);
        const maxGainValue = Math.round(Math.max(...data_pg.gain), 0) +100;
        new Chart(document.getElementById("{canvas_id}"), {{
            type: "line",
            data: {{
                labels: labels_pg,
                datasets: [
                    {{
                        label: 'Performance',
                        data: data_pg.performance,
                        yAxisID: 'y',
                        borderColor: '{COLOR_PERFORMANCE}',
                        backgroundColor: '{COLOR_PERFORMANCE}',
                        borderWidth: 1,
                        pointRadius: 1,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: "Max Performance",
                        data: Array(data_pg.performance.length).fill(data_pg.max_performance),
                        yAxisID: 'y',
                        borderColor: "{COLOR_PERFORMANCE}",
                        borderWidth: 1,
                        borderDash: [6, 6],
                        pointRadius: 0
                    }},
                    {{
                        label: "ZP",
                        data: Array(data_pg.performance.length).fill(0),
                        yAxisID: 'y',
                        borderColor: "{COLOR_PERFORMANCE_ZERO}",
                        borderWidth: 1,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Gain',
                        data: data_pg.gain,
                        yAxisID: 'y1',
                        borderColor: '{COLOR_GAIN}',
                        backgroundColor: '{COLOR_GAIN}',
                        borderWidth: 1,
                        pointRadius: 1,
                        pointHoverRadius: 6,
                        hidden: true
                    }},
                    {{
                        label: "Max Gain",
                        data: Array(data_pg.gain.length).fill(data_pg.max_gain),
                        yAxisID: 'y1',
                        borderColor: "{COLOR_GAIN}",
                        borderWidth: 1,
                        borderDash: [6, 6],
                        pointRadius: 0,
                        hidden: true
                    }},
                    {{
                        label: "ZG",
                        data: Array(data_pg.gain.length).fill(0),
                        yAxisID: 'y1',
                        borderColor: "{COLOR_GAIN_ZERO}",
                        borderWidth: 1,
                        pointRadius: 0,
                        hidden: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            filter: (legendItem) => {{
                                return !["Max Performance", "Max Gain", "ZP", "ZG"].includes(legendItem.text);
                            }}
                        }},
                        onClick: (e, legendItem, legend) => {{
                            const chart = legend.chart;
                            const index = legendItem.datasetIndex;
                            const isVisible = chart.isDatasetVisible(index);
                            chart.setDatasetVisibility(index, !isVisible);
                            if (index === 0 || index === 1) {{ // Perf
                                chart.setDatasetVisibility(1, !isVisible); // Max Performance
                                chart.setDatasetVisibility(2, !isVisible); // ZP
                                chart.setDatasetVisibility(3, isVisible); // Gain
                                chart.setDatasetVisibility(4, isVisible); // Max Gain
                                chart.setDatasetVisibility(5, isVisible); // ZG
                            }}
                            if (index === 3 || index === 4) {{ // Gain
                                chart.setDatasetVisibility(4, !isVisible); // Max Gain
                                chart.setDatasetVisibility(5, !isVisible); // ZP
                                chart.setDatasetVisibility(0, isVisible); // Performance
                                chart.setDatasetVisibility(1, isVisible); // Max Performance
                                chart.setDatasetVisibility(2, isVisible); // ZG
                            }}
                            chart.update();
                        }}
                    }},
                    tooltip: {{
                        filter: (tooltipItem) => {{
                            return !["ZP", "ZG"].includes(tooltipItem.dataset.label);
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month',
                            displayFormats: {{
                                month: 'MMM yy'
                            }}
                        }},
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 30,
                            minRotation: 30,
                            padding: 5
                        }}
                    }},
                    y: {{
                        type: 'linear',
                        position: 'left',
                        min: minPerformanceValue,
                        max: maxPerformanceValue,
                        title: {{
                            display: true,
                            text: 'Performance',
                            color: '{COLOR_PERFORMANCE}'
                        }},
                        grid: {{
                            drawOnChartArea: false
                        }}
                    }},
                    y1: {{
                        type: 'linear',
                        position: 'right',
                        min: minGainValue,
                        max: maxGainValue,
                        title: {{
                            display: true,
                            text: 'Gain',
                            color: '{COLOR_GAIN}'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</div>
    """


def _render_capital_trends_by_amounts(
    capital_trends: list[CapitalTrend]
) -> str:
    labels = [t.date for t in capital_trends]
    values = {
        "amount": [t.amount for t in capital_trends],
        "invested_amount": [t.invested_amount for t in capital_trends]
    }
    values["max_amount"] = max(values["amount"], default=0)
    canvas_id = "capital_trends_amounts_chart"
    return f"""
<div class="chart-container-ct">
    <h3>
        Capital & Invested
    </h3>
    <canvas id="{canvas_id}" />
    <script>
        const labels_ci = {json.dumps(labels)};
        const data_ci = {json.dumps(values)};
        const minValue = Math.round(Math.min(...data_ci.amount, ...data_ci.invested_amount), 0);
        const maxValue = Math.round(Math.max(...data_ci.amount, ...data_ci.invested_amount), 0) +500;
        new Chart(document.getElementById("{canvas_id}"), {{
            type: "line",
            data: {{
                labels: labels_ci,
                datasets: [
                    {{
                        label: 'Capital',
                        data: data_ci.amount,
                        yAxisID: 'y',
                        borderColor: '{COLOR_CAPITAL}',
                        backgroundColor: '{COLOR_CAPITAL}',
                        borderWidth: 1,
                        pointRadius: 1,
                        pointHoverRadius: 6
                    }},
                    {{
                        label: "Max Capital",
                        data: Array(data_ci.amount.length).fill(data_ci.max_amount),
                        borderColor: "{COLOR_CAPITAL}",
                        borderWidth: 1,
                        borderDash: [6, 6],
                        pointRadius: 0
                    }},
                    {{
                        label: 'Investi',
                        data: data_ci.invested_amount,
                        yAxisID: 'y1',
                        borderColor: '{COLOR_INVESTED}',
                        backgroundColor: '{COLOR_INVESTED}',
                        borderWidth: 1,
                        pointRadius: 1,
                        pointHoverRadius: 6
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            filter: (legendItem) => {{
                                return !["Max Capital"].includes(legendItem.text);
                            }}
                        }},
                        onClick: (e, legendItem, legend) => {{
                            const chart = legend.chart;
                            const index = legendItem.datasetIndex;
                            const isVisible = chart.isDatasetVisible(index);
                            chart.setDatasetVisibility(index, !isVisible);
                            if (index === 0) {{ // Capital
                                chart.setDatasetVisibility(1, !isVisible); // Max Capital
                            }}
                            chart.update();
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month',
                            displayFormats: {{
                                month: 'MMM yy'
                            }}
                        }},
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 30,
                            minRotation: 30,
                            padding: 5
                        }}
                    }},
                    y: {{
                        type: 'linear',
                        position: 'left',
                        min: minValue,
                        max: maxValue,
                        title: {{
                            display: true,
                            text: 'Capital',
                            color: '{COLOR_CAPITAL}'
                        }},
                        grid: {{
                            drawOnChartArea: false
                        }}
                    }},
                    y1: {{
                        type: 'linear',
                        position: 'right',
                        min: minValue,
                        max: maxValue,
                        title: {{
                            display: true,
                            text: 'Investi',
                            color: '{COLOR_INVESTED}'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</div>
    """


def _render_positions(
    capital: Capital,
    positions: list[Position],
    products: dict[str, Product],
    config: Config
) -> str:
    rows = []

    total_amount = capital.amount if capital is not None else 0
    total_invested = capital.invested_amount if capital is not None else 0

    total_perf = capital.performance if capital is not None else 0
    total_gain = capital.gain if capital is not None else 0

    total_perf_class = _css_class(capital.performance) if capital is not None else "neutral"
    total_gain_class = _css_class(capital.gain) if capital is not None else "neutral"

    for p in positions:
        guid = p.guid
        name = p.name
        gain = p.amount - p.invested_amount
        weight = (p.amount / total_amount * 100) if total_amount else 0

        product = products.get(guid)
        product_isin = product.isin if product is not None else None
        product_risk = int(product.risk) if product is not None else 0
        product_fee_rate = product.fee_rate if product is not None else None

        perf_class = _css_class(p.performance)
        gain_class = _css_class(gain)

        rows.append(f"""
<tr>
  <td class="left">{escape(name)}</td>
  <td class="right {perf_class}" data-sort="{p.performance:.2f}">
    {p.performance:+.2f} %
  </td>
  <td class="right" data-sort="{p.amount:.2f}">{p.amount:,.2f} €</td>
  <td class="right" data-sort="{p.invested_amount:.2f}">{p.invested_amount:,.2f} €</td>
  <td class="right {gain_class}" data-sort="{gain:.2f}">
    {gain:+,.2f} €
  </td>
  <td class="right details-col" data-sort="{weight:.2f}">
    {weight:+,.2f} %
  </td>
  <td class="center details-col">{_render_risk(product_risk)}</td>
  <td class="right details-col">{_render_feed_rate(product_fee_rate)}</td>
  <td class="center details-col">{_render_mpp_link(guid, config)}{_render_ft_link(product_isin)}</td>
</tr>
""")

    return f"""
<table id="positions-table">
  <thead>
    <tr>
      <th class="left">Total</th>
      <th class="right">Performance</th>
      <th class="right">Current</th>
      <th class="right">Invested</th>
      <th class="right">Gain</th>
      <th class="right details-col">Weight</th>
      <th class="center details-col">Risk</th>
      <th class="right details-col">Feed</th>
      <th class="center details-col">Resources</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
  <tfoot>
    <tr>
      <th class="left">Total</th>
      <th class="right {total_perf_class}">{total_perf:+,.2f} %</th>
      <th class="right">{total_amount:,.2f} €</th>
      <th class="right">{total_invested:,.2f} €</th>
      <th class="right {total_gain_class}">{total_gain:+,.2f} €</th>
      <th class="right details-col"></th>
      <th class="center details-col"></th>
      <th class="right details-col"></th>
      <th class="center details-col"></th>
    </tr>
  </tfoot>
</table>
<div class="right" style="margin-top: 10px; margin-right: 8px;">
    <a href="javascript:void(0);" id="toggle-columns">➕ more details</a>
</div>
<script>
    const button = document.getElementById("toggle-columns");
    button.addEventListener("click", () => {{
        const details = document.querySelectorAll(".details-col");
        const visible = details[0].classList.contains("show");
        details.forEach(col => col.classList.toggle("show"));
        button.textContent = visible ? "➕ more details" : "➖ less details";
    }});
</script>
"""


def _render_product_trends(
    product_trends: dict[str, list[ProductTrend]],
    positions: list[Position]
) -> str:
    html = ""

    for i, t in enumerate(product_trends.values()):
        guid = t[0].guid
        name = t[0].name

        gid = guid.replace("-", "")

        labels = [item.date for item in t]
        values = [item.amount for item in t]

        # Yellow line & yellow point

        initial_investment_buy = _find_order_values_dates(
            "INITIAL_INVESTMENT_BUY_ORDER",
            t,
            labels,
            values)

        initial_investment_buy_value, initial_investment_buy_date = initial_investment_buy[0]

        # Blue points

        monthly_investment_buy = _find_order_values_dates(
            "MONTHLY_INVESTMENT_BUY_ORDER",
            t,
            labels,
            values)

        monthly_dates_js = json.dumps([x[1] for x in monthly_investment_buy])
        monthly_values_js = json.dumps([x[0] for x in monthly_investment_buy])

        # Blue points

        monthly_investment_buy = _find_order_values_dates(
            "FREE_INVESTMENT_BUY_ORDER",
            t,
            labels,
            values)

        free_dates_js = json.dumps([x[1] for x in monthly_investment_buy])
        free_values_js = json.dumps([x[0] for x in monthly_investment_buy])

        # Red points

        exchange_sell = _find_order_values_dates(
            "EXCHANGE_SELL_ORDER",
            t,
            labels,
            values)

        exchange_sell_dates_js = json.dumps([x[1] for x in exchange_sell])
        exchange_sell_values_js = json.dumps([x[0] for x in exchange_sell])

        # Cyan points

        exchange_buy = _find_order_values_dates(
            "EXCHANGE_BUY_ORDER",
            t,
            labels,
            values)

        exchange_buy_dates_js = json.dumps([x[1] for x in exchange_buy])
        exchange_buy_values_js = json.dumps([x[0] for x in exchange_buy])

        canvas_id = f"product_trends_chart_{guid}"

        css_class = "even" if i % 2 == 0 else "odd"

        max_v = max(values) if values else 0

        trend_line_color = COLOR_GREEN if _is_recent_trend_positive(values) else COLOR_RED

        labels_js = json.dumps(labels)
        values_js = json.dumps(values)

        period_performances = _calculate_period_performances(product_trends.get(guid, []))
        position = next((p for p in positions if p.guid == guid))

        html += f"""
<div class="chart-container-pt {css_class}">
    <h3 class="position-title">
        <span>{name}</span>
        <small class="{(_css_class(position.performance) if position.performance is not None else 'neutral')}">
            → {position.performance:,.2f} %
        </small>
    </h3>
    <div>
        {_render_period_performances(period_performances)}
    </div>
    <br/>
    <canvas id="{canvas_id}" />
    <script>
        const labels_{gid} = {labels_js};
        const values_{gid} = {values_js};
        const monthly_dates_{gid} = {monthly_dates_js};
        const monthly_values_{gid} = {monthly_values_js};
        const free_dates_{gid} = {free_dates_js};
        const free_values_{gid} = {free_values_js};
        const exchange_sell_dates_{gid} = {exchange_sell_dates_js};
        const exchange_sell_values_{gid} = {exchange_sell_values_js};
        const exchange_buy_dates_{gid} = {exchange_buy_dates_js};
        const exchange_buy_values_{gid} = {exchange_buy_values_js};
        new Chart(document.getElementById("{canvas_id}"), {{
            type: "line",
            data: {{
                labels: labels_{gid},
                datasets: [
                    {{
                        label: "{name}",
                        data: values_{gid},
                        borderColor: "{trend_line_color}",
                        backgroundColor: "{trend_line_color}",
                        borderWidth: 1,
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.2
                    }},
                    {{
                        label: "Max Value",
                        data: Array({len(values)}).fill({max_v}),
                        borderColor: "{COLOR_GREEN}",
                        borderWidth: 1,
                        borderDash: [6, 6],
                        pointRadius: 0
                    }},
                    {{
                        label: "Initial Investment",
                        data: Array({len(values)}).fill({initial_investment_buy_value}),
                        borderColor: "{COLOR_YELLOW}",
                        backgroundColor: "{COLOR_YELLOW}",
                        borderWidth: 2,
                        borderDash: [6, 6],
                        pointRadius: 0
                    }},
                    {{
                        label: "Initial Investment",
                        data: Array({len(values)}).fill(null).map((_, i) =>
                            labels_{gid}[i] === "{initial_investment_buy_date}" ? values_{gid}[i] : null
                        ),
                        pointBorderColor: "{COLOR_YELLOW}",
                        pointBackgroundColor: "transparent",
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 10,
                    }},
                    {{
                        label: "Monthly Investment",
                        data: Array(labels_{gid}.length).fill(null).map((_, i) => {{
                            const idx = monthly_dates_{gid}.indexOf(labels_{gid}[i]);
                            return idx !== -1 ? monthly_values_{gid}[idx] : null;
                        }}),
                        borderWidth: 2,
                        borderColor: "{COLOR_BLUE}",
                        backgroundColor: "{COLOR_BLUE}",
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        showLine: false
                    }},
                    {{
                        label: "Free Investment",
                        data: Array(labels_{gid}.length).fill(null).map((_, i) => {{
                            const idx = free_dates_{gid}.indexOf(labels_{gid}[i]);
                            return idx !== -1 ? free_values_{gid}[idx] : null;
                        }}),
                        pointBorderColor: "{COLOR_BLUE}",
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 10,
                        showLine: false
                    }},
                    {{
                        label: "Exchange Sell",
                        data: Array(labels_{gid}.length).fill(null).map((_, i) => {{
                            const idx = exchange_sell_dates_{gid}.indexOf(labels_{gid}[i]);
                            return idx !== -1 ? exchange_sell_values_{gid}[idx] : null;
                        }}),
                        pointBorderColor: "{COLOR_RED}",
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 10,
                        showLine: false
                    }},
                    {{
                        label: "Exchange Buy",
                        data: Array(labels_{gid}.length).fill(null).map((_, i) => {{
                            const idx = exchange_buy_dates_{gid}.indexOf(labels_{gid}[i]);
                            return idx !== -1 ? exchange_buy_values_{gid}[idx] : null;
                        }}),
                        pointBorderColor: "{COLOR_CYAN}",
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 10,
                        showLine: false
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month',
                            displayFormats: {{
                                month: 'MMM yy'
                            }}
                        }},
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 30,
                            minRotation: 30,
                            padding: 5
                        }}
                    }}
                }}
            }}
        }});
    </script>
</div>
    """

    return html


def _render_period_performances(
    performances: list[tuple[str, float | None]]
) -> str:
    return "".join(
        f'<span class="period-performance {(_css_class(value) if value is not None else "neutral")}">'
        f'<span class="label">{label}:</span> {value:+.2f} %</span>'
        if value is not None
        else f'<span class="period-performance neutral"><span>{label}</span>: —</span>'
        for label, value in performances)


def _calculate_period_performances(
    product_trends: list[ProductTrend]
) -> list[tuple[str, float | None]]:
    """Return returns relative to the latest available product valuation."""
    dated_trends = sorted(
        (
            (date.fromisoformat(trend.date), trend.amount)
            for trend in product_trends
        ),
        key=lambda trend: trend[0])

    if not dated_trends:
        return [(label, None) for label, _ in PERFORMANCE_PERIODS]

    current_date, current_amount = dated_trends[-1]
    performances = []
    for label, months in PERFORMANCE_PERIODS:
        reference_date = _subtract_months(current_date, months)
        reference = next(
            (trend for trend in reversed(dated_trends) if trend[0] <= reference_date),
            None)
        performance = (
            (current_amount / reference[1] - 1) * 100
            if reference is not None and reference[1]
            else None)
        performances.append((label, performance))
    return performances


def _subtract_months(value: date, months: int) -> date:
    year_offset, month_index = divmod(value.month - months - 1, 12)
    target_year = value.year + year_offset
    target_month = month_index + 1
    target_day = min(value.day, monthrange(target_year, target_month)[1])
    return date(target_year, target_month, target_day)


def _find_order_values_dates(
    tag: str,
    product_trends: list[ProductTrend],
    labels: list,
    values: list
) -> list[tuple[float, str]]:
    orders = [
        t for t in product_trends
        if t.tag == tag
    ]
    result = []
    for order in orders:
        label_idx = labels.index(order.date)
        result.append((values[label_idx], order.date))
    return result


def _is_recent_trend_positive(
    values: list[float],
    window: int = RECENT_TREND_WINDOW
) -> bool:
    window = min(window, len(values))
    recent = values[-window:]
    deltas = [
        recent[i] - recent[i - 1]
        for i in range(1, len(recent))
    ]
    avg_delta = sum(deltas) / len(deltas)
    return avg_delta >= 0


def _render_mpp_link(
    guid: str,
    config: Config
) -> str:
    url = f"https://app.monpetitplacement.fr/comptes/{config.user_investment_account_id}/dashboard/produits-investis/{guid}/compartiments/default"
    return f"""
    <a
        href="{url}"
        class="badge badge-mpp"
        target="_blank"
        rel="noopener noreferrer"
        title="Mon Petit Placement">
        MPP
    </a>
    """


def _render_ft_link(
    isin: str
) -> str:
    if isin is None:
        return ""
    url = f"https://markets.ft.com/data/funds/tearsheet/summary?s={isin}:EUR"
    return f"""
    <a
        href="{url}"
        class="badge badge-ft"
        target="_blank"
        rel="noopener noreferrer"
        title="Financial Times">
        FT
    </a>
    """


def _render_risk(
    value: float
) -> str:
    if value is None or value == 0:
        return "-"
    return int(value)


def _render_feed_rate(
    value: float
) -> str:
    if value is None or value == 0:
        return "-"
    return f"{value} %"


def _css_class(
    value: float
) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"
