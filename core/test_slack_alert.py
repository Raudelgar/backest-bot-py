from slack_notifier import send_slack_alert

test_alert = {
    "symbol": "QQQ",
    "timeframe": "30Min",
    "side": "Long",
    "entry_price": 419.0,
    "stop_loss": 417.5,
    "target": 423.0,
    "confidence": 0.91,
    "mode": "furious",
    "order_size": 1,
    "rank_color": "🟢#1"
}

send_slack_alert(test_alert)
