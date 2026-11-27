"""
market_analyzer.py — Technical Market Analysis Module

Functions:
    calculate_moving_average(data, window)  → SMA values as a list
    detect_trend(stock_prices, window)      → "bullish" | "bearish" | "neutral"

Also includes:
    calculate_ema(data, window)             → Exponential Moving Average
    full_analysis(symbol, period)           → Complete analysis using live data
"""

import json
import statistics
from typing import Literal
import yfinance as yf


# ─── Moving Average Calculators ──────────────────────────────────────────────

def calculate_moving_average(data: list[float], window: int = 14) -> list[float | None]:
    """
    Calculate Simple Moving Average (SMA) for a price series.

    The first (window - 1) values are None because there isn't enough
    preceding data to form a complete window.

    Args:
        data   (list[float]): List of closing prices, oldest first.
        window (int)        : Lookback period (default: 14).

    Returns:
        list[float | None]: SMA value at each position, or None if insufficient data.

    Example:
        calculate_moving_average([10, 11, 12, 13, 14], window=3)
        → [None, None, 11.0, 12.0, 13.0]
    """
    if not data:
        return []
    if window <= 0:
        raise ValueError(f"window must be a positive integer, got {window}")

    sma = []
    for i, _ in enumerate(data):
        if i < window - 1:
            sma.append(None)
        else:
            window_slice = data[i - window + 1 : i + 1]
            sma.append(round(statistics.mean(window_slice), 4))
    return sma


def calculate_ema(data: list[float], window: int = 14) -> list[float | None]:
    """
    Calculate Exponential Moving Average (EMA) for a price series.

    EMA gives more weight to recent prices, making it more reactive
    to new information compared to SMA.

    Args:
        data   (list[float]): List of closing prices, oldest first.
        window (int)        : Lookback period (default: 14).

    Returns:
        list[float | None]: EMA value at each position, or None for the warm-up period.
    """
    if not data:
        return []
    if window <= 0:
        raise ValueError(f"window must be a positive integer, got {window}")

    multiplier = 2 / (window + 1)
    ema: list[float | None] = [None] * (window - 1)

    # Seed with SMA for the first window
    seed = statistics.mean(data[:window])
    ema.append(round(seed, 4))

    for price in data[window:]:
        prev = ema[-1]
        new_ema = (price - prev) * multiplier + prev
        ema.append(round(new_ema, 4))

    return ema


# ─── Trend Detection ─────────────────────────────────────────────────────────

def detect_trend(
    stock_prices: list[float],
    window: int = 14,
    use_ema: bool = False,
    threshold_pct: float = 0.5,
) -> dict:
    """
    Detect the current market trend by comparing the latest price
    against its moving average.

    Logic:
        current_price > MA * (1 + threshold%)  → bullish
        current_price < MA * (1 - threshold%)  → bearish
        otherwise                               → neutral

    Args:
        stock_prices   (list[float]): Closing prices, oldest → newest.
        window         (int)        : MA lookback period (default: 14).
        use_ema        (bool)       : Use EMA instead of SMA (default: False).
        threshold_pct  (float)      : Dead-band % to avoid noisy neutral signals
                                      (default: 0.5%).

    Returns:
        dict: {
            "trend"          : "bullish" | "bearish" | "neutral",
            "current_price"  : float,
            "moving_average" : float,
            "deviation_pct"  : float,   # how far price is from MA (%)
            "window"         : int,
            "ma_type"        : "EMA" | "SMA",
            "data_points"    : int
        }
    """
    if len(stock_prices) < window:
        return {
            "trend": "neutral",
            "current_price": stock_prices[-1] if stock_prices else 0.0,
            "moving_average": None,
            "deviation_pct": 0.0,
            "window": window,
            "ma_type": "EMA" if use_ema else "SMA",
            "data_points": len(stock_prices),
            "error": f"Not enough data: need {window} points, got {len(stock_prices)}",
        }

    # Compute MA series
    ma_series = calculate_ema(stock_prices, window) if use_ema else calculate_moving_average(stock_prices, window)
    ma_type   = "EMA" if use_ema else "SMA"

    # Latest valid MA value
    latest_ma = next((v for v in reversed(ma_series) if v is not None), None)
    if latest_ma is None:
        return {
            "trend": "neutral",
            "current_price": stock_prices[-1],
            "moving_average": None,
            "deviation_pct": 0.0,
            "window": window,
            "ma_type": ma_type,
            "data_points": len(stock_prices),
        }

    current_price = stock_prices[-1]
    deviation_pct = round(((current_price - latest_ma) / latest_ma) * 100, 4)

    # Apply threshold dead-band
    if deviation_pct > threshold_pct:
        trend: Literal["bullish", "bearish", "neutral"] = "bullish"
    elif deviation_pct < -threshold_pct:
        trend = "bearish"
    else:
        trend = "neutral"

    return {
        "trend"         : trend,
        "current_price" : round(current_price, 4),
        "moving_average": round(latest_ma, 4),
        "deviation_pct" : deviation_pct,
        "window"        : window,
        "ma_type"       : ma_type,
        "data_points"   : len(stock_prices),
    }


# ─── Full Live Analysis ───────────────────────────────────────────────────────

def full_analysis(symbol: str, period: str = "3mo", window: int = 14) -> dict:
    """
    Fetch live OHLCV data from yfinance and run a complete
    SMA + EMA trend analysis on real closing prices.

    Args:
        symbol (str) : Ticker, e.g. "AAPL", "TSLA"
        period (str) : yfinance period string (default: "3mo")
        window (int) : MA lookback period (default: 14)

    Returns:
        dict: Full analysis report including both SMA and EMA trends,
              last 5 closing prices, and full MA arrays.
    """
    try:
        ticker = yf.Ticker(symbol)
        df     = ticker.history(period=period)

        if df.empty:
            return {"error": f"No data returned for '{symbol}'", "symbol": symbol}

        prices = [round(p, 4) for p in df["Close"].tolist()]

        sma_series    = calculate_moving_average(prices, window)
        ema_series    = calculate_ema(prices, window)
        sma_trend     = detect_trend(prices, window=window, use_ema=False)
        ema_trend     = detect_trend(prices, window=window, use_ema=True)

        return {
            "symbol"        : symbol.upper(),
            "period"        : period,
            "window"        : window,
            "data_points"   : len(prices),
            "latest_price"  : prices[-1],
            "sma_trend"     : sma_trend,
            "ema_trend"     : ema_trend,
            # Last 5 entries for quick inspection
            "recent_prices" : prices[-5:],
            "recent_sma"    : [v for v in sma_series[-5:]],
            "recent_ema"    : [v for v in ema_series[-5:]],
        }

    except Exception as e:
        return {"error": str(e), "symbol": symbol}


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TREND_ICONS = {"bullish": "🟢 BULLISH", "bearish": "🔴 BEARISH", "neutral": "🟡 NEUTRAL"}

    # ── Test 1: Simple synthetic data
    print("\n" + "═" * 60)
    print("  📐  Test 1 — Synthetic Price Data")
    print("═" * 60)

    prices_bull = [100, 101, 102, 103, 104, 105, 106, 107, 108, 110, 112, 115, 118, 120, 125]
    prices_bear = [125, 123, 120, 117, 114, 111, 108, 106, 104, 102, 101, 100, 99, 98, 95]
    prices_flat = [100, 101, 100, 99, 101, 100, 101, 100, 99, 100, 101, 100, 99, 100, 101]

    for label, prices in [("Upward (bullish?)", prices_bull),
                           ("Downward (bearish?)", prices_bear),
                           ("Sideways (neutral?)", prices_flat)]:
        result = detect_trend(prices, window=7)
        sma    = calculate_moving_average(prices, window=7)
        print(f"\n  {label}")
        print(f"  Prices (last 5) : {prices[-5:]}")
        print(f"  SMA (last 5)    : {sma[-5:]}")
        print(f"  → Trend         : {TREND_ICONS[result['trend']]}")
        print(f"  → Current Price : {result['current_price']}  |  SMA-7: {result['moving_average']}")
        print(f"  → Deviation     : {result['deviation_pct']:+.2f}%")

    # ── Test 2: Live stock data
    print("\n\n" + "═" * 60)
    print("  📈  Test 2 — Live Market Analysis (yfinance)")
    print("═" * 60)

    for sym in ["AAPL", "TSLA", "NVDA"]:
        report = full_analysis(sym, period="3mo", window=14)
        if "error" in report:
            print(f"\n  {sym}: ERROR — {report['error']}")
            continue

        sma_t = report["sma_trend"]
        ema_t = report["ema_trend"]
        print(f"\n  🏷  {report['symbol']}  ({report['period']}, window={report['window']})")
        print(f"  Latest Price   : ${report['latest_price']}")
        print(f"  Recent Prices  : {report['recent_prices']}")
        print(f"  Recent SMA-14  : {report['recent_sma']}")
        print(f"  Recent EMA-14  : {report['recent_ema']}")
        print(f"  SMA Trend      : {TREND_ICONS[sma_t['trend']]}  "
              f"(price {sma_t['current_price']} vs SMA {sma_t['moving_average']}, "
              f"dev {sma_t['deviation_pct']:+.2f}%)")
        print(f"  EMA Trend      : {TREND_ICONS[ema_t['trend']]}  "
              f"(price {ema_t['current_price']} vs EMA {ema_t['moving_average']}, "
              f"dev {ema_t['deviation_pct']:+.2f}%)")
        print(f"  JSON (SMA)     : {json.dumps({k:v for k,v in sma_t.items()})}")
