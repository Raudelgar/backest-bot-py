# RSI-2 Backtesting & Alert System

A Python-based RSI-2 mean reversion trading system designed to generate **daily trading alerts** via Slack, using **historical data from Alpaca**, customizable parameters, and capital allocation modes.

---

## 🔍 Project Purpose

The goal of this system is to **generate actionable daily alerts** for top trading setups using a mean reversion strategy (RSI-2) on selected US stocks and ETFs.

---

## 🧠 Strategy Logic

- **Entry Long**: RSI < threshold AND price > SMA100
- **Entry Short**: RSI > (100 - threshold) AND price < SMA100
- **Exit**: Stop loss or limit target is hit
- **Time filter**: US session hours only (2PM–10PM UTC)
- **Capital Allocation Modes**:
  - `vacation`: full equity in one position
  - `conservative`: equal split
  - `furious`: ranked weighted split

---

## 🔔 Alert Structure

Alerts are generated once per daily script run and are valid only for the **current day**.

**Each alert includes:**

- Symbol, Timeframe, Side
- Entry Price (limit), SL, Target
- Confidence Score (0 to 1.0)
- Mode (vacation/conservative/furious)
- Order Size (1 contract)
- Rank Color (🟢 #1, 🔵 #2, 🔴 #3+)

Alerts are saved to:

```bash
alerts.json
```

And sent to Slack (desktop + mobile) using:

```bash
SLACK_WEBHOOK_URL
```

---

## 🛠️ Developer Setup

### Environment

- Python 3.12+
- `.venv` virtual environment
- `.env` file with:
  ```env
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
  ```

### File Structure

- `main.py`: Orchestrates backtest + alerts
- `config.py`: Parameters + stock lists
- `generate_alert.py`: Writes alerts.json
- `core/backtester.py`: Strategy logic
- `data/fetcher.py`: Pulls bars from Alpaca
- `core/slack_notifier.py`: Sends alert to Slack

### Clean & Start Fresh

Before each full run:

```bash
python3 prepare_for_run.py
python3 main.py
```

---

## 🧪 Testing

To test on one stock + one TF:

```python
STOCKS = ["QQQ"]
TIMEFRAMES = ["30Min"]
```

Use `alerts.json` to preview, or force generate:

```bash
python generate_alert.py
```

---

## 📬 Slack Setup

- Go to [Slack Apps](https://api.slack.com/apps)
- Create a **new app** > **Incoming Webhooks**
- Choose your channel and copy the **webhook URL**
- Set this URL in your `.env`

To test alert delivery:

```python
send_slack_alert(alert)
```

---

## ⏱️ Alert Timing

Currently, alerts are **triggered right after backtest**, based on what **could** be traded that day. No intra-day execution.

---

## 🛣️ Roadmap

### v2 Ideas:

- Intra-day live alert engine
- MAX_DISTANCE_FROM_PRICE control
- Trend confirmation filters
- Auto-execution via Alpaca paper trading
- Pine Script mirror visualization on TradingView

---

## 👥 Authors

- Dev: Raudel Garcia
- Stack: Python + Slack + Alpaca + Rich + TQDM

---
