#!/usr/bin/env python3

import os
# python3 prepare_for_run.py

FILES_TO_CLEAR = [
    "trade_log.csv",
    "trades_long.csv",
    "trades_short.csv",
    "alerts.json",
    "backtest.log"
]

for file in FILES_TO_CLEAR:
    if os.path.exists(file):
        with open(file, "w") as f:
            f.write("")
        print(f"✅ Cleared {file}")
    else:
        print(f"⚠️ {file} not found, skipping.")

print("✅ Ready for fresh run.")
