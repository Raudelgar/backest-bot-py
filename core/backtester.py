import pandas as pd
import numpy as np
from datetime import datetime

def run_backtest(
    df: pd.DataFrame,
    rsi_entry: int,
    stop_mult: float,
    limit_mult: float,
    equity: float,
    use_session: bool = True,
    capital: float = 0.0,
    enable_short: bool = True
):
    position = None  # None, 'long', or 'short'
    entry_price = 0
    stop_price = 0
    limit_price = 0
    entry_time = None
    max_drawdown = 0
    position_size = 0

    trades = []
    gross_profit = 0
    gross_loss = 0
    running_pnl = 0
    peak_equity = capital

    for i in range(1, len(df)):
        row = df.iloc[i]
        hh = row['close_time'].tz_convert("America/New_York").hour
        in_sess = (not use_session) or (14 <= hh < 22)

        go_long = (row['rsi'] < rsi_entry) and (row['close'] > row['sma100']) and in_sess
        go_short = (row['rsi'] > (100 - rsi_entry)) and (row['close'] < row['sma100']) and in_sess

        if go_long and go_short:
            long_strength = rsi_entry - row['rsi']
            short_strength = row['rsi'] - (100 - rsi_entry)
            go_long = long_strength > short_strength
            go_short = not go_long

        # ENTRY
        if position is None:
            if go_long:
                position = 'long'
                entry_price = row['close']
                position_size = capital / entry_price
                stop_price = entry_price - stop_mult * row['atr']
                limit_price = entry_price + limit_mult * row['atr']
                entry_time = row['close_time']
            elif enable_short and go_short:
                position = 'short'
                entry_price = row['close']
                position_size = capital / entry_price
                stop_price = entry_price + stop_mult * row['atr']
                limit_price = entry_price - limit_mult * row['atr']
                entry_time = row['close_time']
            else:
                continue

        # EXIT
        elif position == 'long':
            if row['low'] <= stop_price:
                exit_price = stop_price
            elif row['high'] >= limit_price:
                exit_price = limit_price
            else:
                continue

            exit_time = row['close_time']
            pnl = (exit_price - entry_price) * position_size
            running_pnl += pnl
            gross_profit += pnl if pnl > 0 else 0
            gross_loss += abs(pnl) if pnl < 0 else 0
            trades.append((entry_time, exit_time, entry_price, capital, pnl, "long"))
            position = None

            # Re-evaluate entry after exit
            go_long = (row['rsi'] < rsi_entry) and (row['close'] > row['sma100']) and in_sess
            go_short = (row['rsi'] > (100 - rsi_entry)) and (row['close'] < row['sma100']) and in_sess
            if go_long and go_short:
                long_strength = rsi_entry - row['rsi']
                short_strength = row['rsi'] - (100 - rsi_entry)
                go_long = long_strength > short_strength
                go_short = not go_long

            if go_short and enable_short:
                position = 'short'
                entry_price = row['close']
                position_size = capital / entry_price
                stop_price = entry_price + stop_mult * row['atr']
                limit_price = entry_price - limit_mult * row['atr']
                entry_time = row['close_time']

        elif position == 'short':
            if row['high'] >= stop_price:
                exit_price = stop_price
            elif row['low'] <= limit_price:
                exit_price = limit_price
            else:
                continue

            exit_time = row['close_time']
            pnl = (entry_price - exit_price) * position_size
            running_pnl += pnl
            gross_profit += pnl if pnl > 0 else 0
            gross_loss += abs(pnl) if pnl < 0 else 0
            trades.append((entry_time, exit_time, entry_price, capital, pnl, "short"))
            position = None

            # Re-evaluate entry after exit
            go_long = (row['rsi'] < rsi_entry) and (row['close'] > row['sma100']) and in_sess
            go_short = (row['rsi'] > (100 - rsi_entry)) and (row['close'] < row['sma100']) and in_sess
            if go_long and go_short:
                long_strength = rsi_entry - row['rsi']
                short_strength = row['rsi'] - (100 - rsi_entry)
                go_long = long_strength > short_strength
                go_short = not go_long

            if go_long:
                position = 'long'
                entry_price = row['close']
                position_size = capital / entry_price
                stop_price = entry_price - stop_mult * row['atr']
                limit_price = entry_price + limit_mult * row['atr']
                entry_time = row['close_time']

        # DRAWDOWN
        current_equity = capital + running_pnl
        peak_equity = max(peak_equity, current_equity)
        drawdown = peak_equity - current_equity
        max_drawdown = max(max_drawdown, drawdown)

    # LOG TRADES
    with open("trades_long.csv", "a") as f_long, open("trades_short.csv", "a") as f_short:
        for entry_time, exit_time, entry_price, cap, pnl, side in trades:
            if side == "long":
                f_long.write(f"{entry_time},{exit_time},{cap:.2f},{pnl:.2f}\n")
            else:
                f_short.write(f"{entry_time},{exit_time},{cap:.2f},{pnl:.2f}\n")

    return running_pnl, max_drawdown, trades, gross_profit, gross_loss
