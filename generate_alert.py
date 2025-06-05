import json
from datetime import datetime, timezone

def generate_alerts(symbol: str, timeframe: str, results: list, mode: str = "Furious", stop_mult: float = 1.0, limit_mult: float = 2.0):
    alerts = []
    for idx, result in enumerate(results):
        pnl, max_dd, trades, gross_profit, gross_loss = result
        if not trades:
            continue

        entry_time, exit_time, entry_price, capital, pnl_value, side = trades[-1]
        confidence = round(min(max(pnl_value / capital, 0), 1.0), 2)

        rank = idx + 1
        if rank == 1:
            rank_color = f"🟢#{rank}"
        elif rank == 2:
            rank_color = f"🔵#{rank}"
        else:
            rank_color = f"🔴#{rank}"

        alert = {
            "symbol": symbol,
            "timeframe": timeframe,
            "side": side.title(),
            "entry_price": round(entry_price, 2),
            "stop_loss": round(entry_price - stop_mult, 2) if side == "long" else round(entry_price + stop_mult, 2),
            "target": round(entry_price + limit_mult, 2) if side == "long" else round(entry_price - limit_mult, 2),
            "confidence": confidence,
            "mode": mode,
            "order_size": 1,
            "rank_color": rank_color,
            "alert_time": datetime.now(timezone.utc).isoformat()
        }
        alerts.append(alert)

    return alerts
