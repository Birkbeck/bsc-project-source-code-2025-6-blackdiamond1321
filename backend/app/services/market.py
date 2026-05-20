"""Live quotes for stocks and crypto
Take the last 5 days of daily closes from yfinance, uses the most recent
to calculate the percentage change. Cached in memory for 30 seconds"""
import time

# Refresh cache to update prices
CACHE_TTL = 30


STOCKS = [
    ("AAPL", "Apple"),
    ("GOOGL", "Alphabet"),
    ("NFLX", "Netflix"),
    ("KO", "Coca-Cola"),
    ("MCD", "McDonald's"),
]

CRYPTO = [
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
    ("SOL-USD", "Solana"),
    ("BNB-USD", "BNB"),
    ("DOGE-USD", "Dogecoin"),
]


def _fetch_quotes(catalogue: list[tuple]) -> list[dict]:
    """Take 5 days to calculate the percentage change and convert price in GBP.
    Yahoo's GBPUSD=X is USD per 1 GBP, so invert it to get GBP per 1 USD"""
    import yfinance as yf

    symbols = [sym for sym, _ in catalogue]

    df = yf.download(
        tickers=" ".join(symbols + ["GBPUSD=X"]),
        period="5d", interval="1d",
        progress=False, auto_adjust=False, threads=False,
    )

    try:
        gbp_per_usd = 1 / float(df["Close"]["GBPUSD=X"].dropna().iloc[-1])
    except Exception:
        gbp_per_usd = 1.0   # keep rate in USD if error happen

    out = []
    for sym, name in catalogue:
        try:
            closes = df["Close"][sym].dropna()
            if not len(closes):
                continue
            last = float(closes.iloc[-1])
            prev = float(closes.iloc[-2]) if len(closes) >= 2 else last
            out.append({
                "symbol": sym,
                "name": name,
                "price": round(last * gbp_per_usd, 2),
                "change_pct": round((last - prev) / prev * 100, 2) if prev else 0,
                "currency": "GBP",
            })
        except Exception:
            continue # skip if a gap present
    return out


class MarketService:
    """Cached quotes for the stock and crypto"""

    def __init__(self):
        self._cache: dict = {}

    def get_stocks(self): return self._cached("stocks", STOCKS)
    def get_crypto(self): return self._cached("crypto", CRYPTO)

    def _cached(self, key: str, catalogue: list[tuple]) -> dict:
        now = time.time()
        entry = self._cache.get(key)
        if entry and now - entry[0] < CACHE_TTL:
            return {"quotes": entry[1], "fetched_at": entry[0], "stale": False}

        try:
            quotes = _fetch_quotes(catalogue)
        except Exception:
            quotes = []
        self._cache[key] = (now, quotes)
        return {"quotes": quotes, "fetched_at": now, "stale": False}