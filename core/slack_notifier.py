import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(alert):
    if not SLACK_WEBHOOK_URL:
        print("No Slack webhook configured.")
        return

    color = {
        "Long": "🟢",
        "Short": "🔴",
        "Exit Long": "🔵",
        "Exit Short": "🟡"
    }.get(alert["side"], "⚪")

    message = f"""{color} *{alert['symbol']} {alert['timeframe']}* – {alert['side']}
> Entry: *{alert['entry_price']}*, SL: {alert['stop_loss']}, Target: {alert['target']}
> Confidence: *{alert['confidence']}* ({alert['rank_color']})
> Mode: {alert['mode'].title()}, Order Size: {alert['order_size']}
"""

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

    if response.status_code != 200:
        print(f"Slack alert failed: {response.status_code}, {response.text}")
