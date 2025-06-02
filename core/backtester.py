import pandas as pd
import numpy as np
from typing import List, Tuple

def run_backtest(
    df: pd.DataFrame,
    rsi_entry: float,
    stop_mult: float,
    limit_mult: float,
    equity: float,
    use_session: bool = True,
    capital: float = 0.0
) -> Tuple[float, float, List[Tuple[pd.Timestamp, float, float]], float, float]:
    pnl = 0.0
    peak = 0.0
    max_dd = 0.0
    in_position = False
    is_short = False
    entry = stop = limit = np.nan
    position_size = 0
    trades = []

    gross_profit = 0.0
    gross_loss = 0.0

    for _, bar in df.iterrows():
        hh = bar['close_time'].tz_convert("America/New_York").hour
        in_sess = (not use_session) or (14 <= hh < 22)

        go_long = (bar['rsi'] < rsi_entry) and (bar['close'] > bar['sma100']) and in_sess
        go_short = (bar['rsi'] > (100 - rsi_entry)) and (bar['close'] < bar['sma100']) and in_sess

        # Resolve conflict if both LONG and SHORT fire
        if go_long and go_short:
            long_strength = rsi_entry - bar['rsi']
            short_strength = bar['rsi'] - (100 - rsi_entry)
            go_long = long_strength > short_strength
            go_short = not go_long

        # Enter new position if flat
        if not in_position:
            if go_long:
                in_position = True
                is_short = False
                entry = bar['close']
                position_size = capital / entry
                stop = entry - stop_mult * bar['atr14']
                limit = entry + limit_mult * bar['atr14']
                continue
            elif go_short:
                in_position = True
                is_short = True
                entry = bar['close']
                position_size = capital / entry
                stop = entry + stop_mult * bar['atr14']
                limit = entry - limit_mult * bar['atr14']
                continue

        # Exit condition
        if in_position:
            hit_stop = bar['high'] >= stop if is_short else bar['low'] <= stop
            hit_limit = bar['low'] <= limit if is_short else bar['high'] >= limit

            if hit_stop and hit_limit:
                exit_px = stop
            elif hit_stop:
                exit_px = stop
            elif hit_limit:
                exit_px = limit
            else:
                exit_px = bar['close']

            # On exit
            direction = -1 if is_short else 1
            trade_pnl = direction * (exit_px - entry) * position_size
            pnl += trade_pnl
            trades.append((bar['close_time'], entry, exit_px))

            if trade_pnl > 0:
                gross_profit += trade_pnl
            else:
                gross_loss += abs(trade_pnl)

            in_position = False

            # 🌀 Ride the wave — check for new signal on same bar
            go_long = (bar['rsi'] < rsi_entry) and (bar['close'] > bar['sma100']) and in_sess
            go_short = (bar['rsi'] > (100 - rsi_entry)) and (bar['close'] < bar['sma100']) and in_sess

            if go_long and go_short:
                long_strength = rsi_entry - bar['rsi']
                short_strength = bar['rsi'] - (100 - rsi_entry)
                go_long = long_strength > short_strength
                go_short = not go_long

            if go_long:
                in_position = True
                is_short = False
                entry = bar['close']
                position_size = capital / entry
                stop = entry - stop_mult * bar['atr14']
                limit = entry + limit_mult * bar['atr14']
            elif go_short:
                in_position = True
                is_short = True
                entry = bar['close']
                position_size = capital / entry
                stop = entry + stop_mult * bar['atr14']
                limit = entry - limit_mult * bar['atr14']

        peak = max(peak, pnl)
        max_dd = max(max_dd, peak - pnl)

    return pnl, max_dd, trades, gross_profit, gross_loss
