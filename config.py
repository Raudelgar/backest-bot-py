from datetime import datetime, timedelta, timezone

# STOCKS = ["SPY", "QQQ", "XLK", "XLF", "XLP", "TLT", "AAPL", "AMZN", "MSFT", "GOOG"]
STOCKS = ["QQQ", "SPY", "TSLA", "AAPL", "NVDA"]
# STOCKS = ["QQQ"]

TIMEFRAMES = ["5Min", "15Min", "30Min", "1Hour", "2Hour", "4Hour"]
# TIMEFRAMES = ["30Min"]

# Capital allocation mode: "furious", "conservative", or "vacation"
MODE = "furious"

RSI_SHORT_ENTRY = None  # for SHORT trades
ENABLE_SHORT = True   # flag to enable/disable SHORT logic


# ✅ Use timezone-aware UTC datetime
DATE_TO = datetime.now(timezone.utc).date()
DATE_FROM = DATE_TO - timedelta(weeks=7)

RSI_MID = [20, 25, 30]                     # Sweep 20, 25, 30
LIMIT_MULTIPLIERS = list(range(1, 26))     # Sweep list(range(1, 26))
STOP_MULTIPLIER = [0.5, 1.0, 1.5]          # Sweep 0.5, 1.0, 1.5

EQUITY = 50000
USE_SESSION = True

# 🔑 API credentials
API_KEY = "PKWMYKDH8EP7776RG2AP"
SECRET_KEY = "efbaKlNDkNTwMHxFlak8tm9a4rYRr1hLBZHpKBYJ"
BASE_URL = "https://data.alpaca.markets"
