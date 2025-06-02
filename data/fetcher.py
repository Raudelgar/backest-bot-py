import pandas as pd
import time
import logging
from alpaca_trade_api.rest import REST
from config import API_KEY, SECRET_KEY, BASE_URL

logger = logging.getLogger()

api = REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

def fetch_data(symbol: str, timeframe: str, date_from, date_to, max_retries=3) -> pd.DataFrame:
    for attempt in range(max_retries):
        try:
            bars = api.get_bars(
                symbol=symbol,
                timeframe=timeframe,
                start=date_from.isoformat(),
                end=date_to.isoformat(),
                adjustment='raw',
                feed='iex'
            ).df.reset_index()

            if bars.empty:
                raise ValueError(f"No data returned for {symbol} {timeframe}.")

            # bars = bars.rename(columns={'timestamp': 'time'})
            # bars['time'] = pd.to_datetime(bars['time'], utc=True)
            bars = bars.rename(columns={'timestamp': 'close_time'})
            bars['close_time'] = pd.to_datetime(bars['close_time'], utc=True)


            logger.info(f"Fetched {len(bars)} bars for {symbol} {timeframe}")

            return bars

        except Exception as e:
            logger.warning(f"[fetch_data] Error for {symbol} {timeframe}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in 3s ({max_retries - attempt - 1} attempts left)...")
                time.sleep(3)
            else:
                logger.error(f"Failed to fetch {symbol} {timeframe} after {max_retries} attempts.")
                raise RuntimeError(f"Failed to fetch {symbol} {timeframe}") from e
