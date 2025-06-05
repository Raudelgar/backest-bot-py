import time
import itertools
import logging
from pandas_market_calendars import get_calendar
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
from config import (
    STOCKS, TIMEFRAMES, STOP_MULTIPLIER, LIMIT_MULTIPLIERS, RSI_MID,
    DATE_FROM, DATE_TO, EQUITY, USE_SESSION, MODE,
    ENABLE_SHORT, RSI_SHORT_ENTRY
)

from data.fetcher import fetch_data
from strategies.rsi2_mean_rev import prepare_data
from core.backtester import run_backtest
from generate_alert import generate_alerts
from core.slack_notifier import send_slack_alert
import json

# ──────────────────────────────
# Logging Setup
logging.basicConfig(
    filename="backtest.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger()
console = Console()

# python main.py
def get_allocation(symbol_rank: int, total_symbols: int, equity: float) -> float:
    if MODE == "vacation":
        return equity  # Use 100% equity in one trade
    elif MODE == "conservative":
        return equity / total_symbols  # Equal split
    elif MODE == "furious":
        # Allocate based on rank (better ranks get more)
        return equity * ((total_symbols - symbol_rank + 1) / (total_symbols * (total_symbols + 1) / 2))
    else:
        raise ValueError(f"Unknown mode: {MODE}")

# Compute actual trading days between DATE_FROM and DATE_TO using NYSE calendar
nyse = get_calendar("NYSE")
schedule = nyse.schedule(start_date=DATE_FROM, end_date=DATE_TO)
trading_days_count = len(schedule)

def main():
    results = []
    total_combinations = len(STOCKS) * len(TIMEFRAMES) * len(STOP_MULTIPLIER) * len(LIMIT_MULTIPLIERS) * len(RSI_MID)
    progress_count = 1

    combinations = list(itertools.product(STOCKS, TIMEFRAMES, STOP_MULTIPLIER, LIMIT_MULTIPLIERS, RSI_MID))

    for symbol, tf, stop_mult, limit_mult, rsi_mid in tqdm(combinations, desc="Backtesting"):
        print(f"[{progress_count}/{total_combinations}] Running: {symbol} {tf} | Stop: {stop_mult}, Limit: {limit_mult}, RSI: {rsi_mid}")
        progress_count += 1
        capital = EQUITY  # or EQUITY / len(STOCKS) if you'd prefer uniform conservative allocation

        try:
            bars = fetch_data(symbol, tf, DATE_FROM, DATE_TO)
            if bars is None or bars.empty:
              raise ValueError("No data returned for backtest.")
            df = prepare_data(bars)
            backtest_result = run_backtest(
                df=df,
                rsi_entry=rsi_mid,
                stop_mult=stop_mult,
                limit_mult=limit_mult,
                equity=EQUITY,
                use_session=USE_SESSION,
                capital=capital,
                enable_short=ENABLE_SHORT,
                # rsi_short_entry=RSI_SHORT_ENTRY,
            )
            pnl, max_dd, trades, gross_profit, gross_loss = backtest_result
            pf = gross_profit / max(1e-6, gross_loss)
            risk_adjusted_pnl = pnl / max(1e-6, max_dd)

            if pf >= 2 and len(trades) >= 10:
                results.append((
                  symbol, tf, limit_mult, stop_mult, rsi_mid,
                  pnl, max_dd, len(trades), pf, risk_adjusted_pnl,
                  capital,  # allocation (may be recomputed later)
                  trades, gross_profit, gross_loss
                ))
        except Exception as e:
            msg = f"Error with {symbol} {tf} x{limit_mult} => {e}"
            console.print(f"[red]{msg}[/red]")
            logger.exception(msg)

        time.sleep(0.5)  # avoid rate-limiting

    # Group by symbol and keep best by risk-adjusted PnL
    best_by_symbol = {}
    for r in results:
        symbol = r[0]
        if symbol not in best_by_symbol or r[9] > best_by_symbol[symbol][9]:
            best_by_symbol[symbol] = r

    # Final sort and display
    final_results = sorted(best_by_symbol.values(), key=lambda x: x[9], reverse=True)

    # Best strategies already selected
    sorted_results = sorted(best_by_symbol.values(), key=lambda x: x[-1], reverse=True)


    # Prepare table rows with capital allocation
    results_with_allocation = []  # <-- renamed to avoid clashing

    for rank, result in enumerate(sorted_results, 1):
        symbol = result[0]
        allocation = get_allocation(rank, len(sorted_results), EQUITY)
        result = list(result)
        result.append(round(allocation, 2))
        results_with_allocation.append(result)

    # Format dates for the title
    date_from_str = DATE_FROM.strftime("%Y-%m-%d")
    date_to_str = DATE_TO.strftime("%Y-%m-%d")

    table = Table(title=f"Top Backtest Results ({date_from_str} to {date_to_str})", show_lines=True)
    table.add_column("Symbol")
    table.add_column("TF")
    table.add_column("Limit xATR")
    table.add_column("Stop xATR")
    table.add_column("RSI")
    table.add_column("Net P&L")
    table.add_column("Max DD")
    table.add_column("Trades")
    table.add_column("Profit Factor")
    table.add_column("Risk-Adjusted P&L")
    table.add_column("Capital")

    for r in results_with_allocation[:5]:
      table.add_row(
          r[0], r[1], f"{r[2]:.1f}", f"{r[3]:.1f}", str(r[4]),
          f"${r[5]:.2f}", f"${r[6]:.2f}", str(r[7]),
          f"{r[8]:.2f}", f"{r[9]:.2f}", f"${r[10]:,.2f}"
      )

    console.print(table)

    # Sum total net P&L and capital used
    total_net_pnl = sum(r[5] for r in results_with_allocation)
    total_allocated_capital = sum(r[10] for r in results_with_allocation)

    # Average daily return = total net P&L / trading days
    avg_daily_return = total_net_pnl / trading_days_count
    avg_daily_return_pct = (avg_daily_return / total_allocated_capital) * 100

    # Projected returns
    monthly_return = avg_daily_return * 21
    monthly_return_pct = avg_daily_return_pct * 21

    yearly_return = avg_daily_return * 252
    yearly_return_pct = avg_daily_return_pct * 252

    # Display
    console.print(f"\n[bold green]Projected Daily Return:[/bold green] ${avg_daily_return:.2f} ({avg_daily_return_pct:.2f}%)")
    console.print(f"[bold green]Projected Monthly Return:[/bold green] ${monthly_return:.2f} ({monthly_return_pct:.2f}%)")
    console.print(f"[bold green]Projected Yearly Return:[/bold green] ${yearly_return:.2f} ({yearly_return_pct:.2f}%)")


    with open("trade_log.csv", "w") as f:
        f.write("Entry Time,Exit Time,Size,PNL\n")

    # Run alerts for top 5 ranked symbols
    all_alerts = []

    for result in final_results[:5]:
        symbol, timeframe = result[0], result[1]
        trades = result[11]
        gross_profit = result[12]
        gross_loss = result[13]
        pnl = result[5]
        max_dd = result[6]

        alert_result = [(
            pnl,
            max_dd,
            trades,
            gross_profit,
            gross_loss
        )]

        alerts = generate_alerts(symbol, timeframe, alert_result, mode=MODE.lower(), stop_mult=result[3], limit_mult=result[2])
        all_alerts.extend(alerts)

    # Save all alerts to alerts.json
    with open("alerts.json", "w") as f:
        json.dump(all_alerts, f, indent=2)

    console.print(f"\n✅ Saved {len(all_alerts)} alert(s) to alerts.json")

    # Send Slack alerts
    for alert in all_alerts:
        send_slack_alert(alert)


if __name__ == "__main__":
    main()
