import pandas as pd
import numpy as np

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    chg = df["close"].diff()
    up = chg.clip(lower=0)
    down = (-chg).clip(lower=0)

    df["rsi"] = 100 - 100 / (1 + up.rolling(2).sum() / down.rolling(2).sum().replace(0, np.nan))
    df["sma100"] = df["close"].rolling(100).mean()
    df["atr"] = (
        np.maximum(
            abs(df["high"] - df["low"]),
            abs(df["high"] - df["close"].shift()),
            abs(df["low"] - df["close"].shift())
        ).rolling(14).mean()
    )

    return df.dropna(subset=["rsi", "sma100", "atr"]).reset_index(drop=True)
