import json

def generate_alerts(symbol: str, timeframe: str, results: list, stop_mult: float, limit_mult: float, mode: str = "Furious"):
    alerts = []
    for idx, result in enumerate(results):
        pnl, max_dd, trades, gross_profit, gross_loss = result
        if not trades:
            continue

        entry_time, exit_time, entry_price, capital, pnl_value, side = trades[-1]
        # entry_price = trades[-1][1] if side == "long" else trades[-1][1]

        # Estimate confidence: higher profit = higher confidence
        confidence = round(min(max(pnl_value / capital, 0), 1.0), 2)

        # Rank color (mock rank based on order in list for now)
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
            "side": side.title(),  # "Long", "Short"
            "entry_price": round(entry_price, 2),
            "stop_loss": round(entry_price - stop_mult, 2) if side == "long" else round(entry_price + stop_mult, 2),
            "target": round(entry_price + limit_mult, 2) if side == "long" else round(entry_price - limit_mult, 2),
            "confidence": confidence,
            "mode": mode,
            "order_size": 1,
            "rank_color": rank_color
        }
        alerts.append(alert)

    with open("alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)

    print(f"✅ Saved {len(alerts)} alert(s) to alerts.json")
