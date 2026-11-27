"""
stock_api.py — Financial data module using yfinance.

Functions:
    get_stock_price(symbol)          → Current price snapshot as JSON
    get_stock_history(symbol, period) → OHLCV history as JSON
"""

import yfinance as yf
import json
from typing import Union


def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest price snapshot for a given stock symbol.

    Args:
        symbol (str): Stock ticker, e.g. "AAPL", "TSLA"

    Returns:
        dict: {
            "symbol": str,
            "name": str,
            "price": float,
            "open": float,
            "high": float,
            "low": float,
            "volume": int,
            "change": float,       # absolute change from previous close
            "change_pct": float,   # percentage change (%)
            "currency": str
        }
    """
    try:
        ticker = yf.Ticker(symbol)

        # Price data comes from the chart endpoint (history), which works from
        # cloud hosts; the quoteSummary endpoint behind `.info` is often blocked.
        hist = ticker.history(period="5d")
        if hist.empty:
            return {"error": f"No price data found for {symbol.upper()}", "symbol": symbol.upper()}

        last = hist.iloc[-1]
        price = float(last["Close"])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else 0.0
        change = round(price - prev_close, 4) if prev_close else 0.0
        change_pct = round((change / prev_close) * 100, 4) if prev_close else 0.0

        # Optional metadata — best effort only.
        name, currency = symbol.upper(), None
        try:
            currency = ticker.fast_info.get("currency")
        except Exception:
            pass
        try:
            info = ticker.info or {}
            name = info.get("longName") or info.get("shortName") or name
            currency = currency or info.get("currency")
        except Exception:
            pass
        if not currency:
            currency = "INR" if symbol.upper().endswith((".NS", ".BO")) else "USD"

        return {
            "symbol": symbol.upper(),
            "name": name,
            "price": round(price, 4),
            "open": round(float(last["Open"]), 4),
            "high": round(float(last["High"]), 4),
            "low": round(float(last["Low"]), 4),
            "volume": int(last["Volume"]),
            "change": change,
            "change_pct": change_pct,
            "currency": currency,
        }

    except Exception as e:
        return {"error": str(e), "symbol": symbol.upper()}


def get_stock_history(symbol: str, period: str = "7d") -> dict:
    """
    Fetch OHLCV historical data for a given stock symbol.

    Args:
        symbol (str): Stock ticker, e.g. "AAPL", "TSLA"
        period (str): Data period — valid values:
                      "1d", "5d", "7d", "1mo", "3mo", "6mo",
                      "1y", "2y", "5y", "10y", "ytd", "max"

    Returns:
        dict: {
            "symbol": str,
            "period": str,
            "records": int,
            "history": [
                {
                    "date": str,
                    "open": float,
                    "high": float,
                    "low": float,
                    "close": float,
                    "volume": int
                },
                ...
            ]
        }
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return {
                "error": f"No historical data found for '{symbol}' with period='{period}'.",
                "symbol": symbol.upper(),
                "period": period,
            }

        history = []
        for date, row in df.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            })

        return {
            "symbol": symbol.upper(),
            "period": period,
            "records": len(history),
            "history": history,
        }

    except Exception as e:
        return {"error": str(e), "symbol": symbol.upper(), "period": period}


# ─── Quick demo if run directly ─────────────────────────────────────────────

if __name__ == "__main__":
    for sym in ["AAPL", "TSLA", "GOOGL"]:
        print(f"\n{'='*50}")
        print(f"  Stock Price — {sym}")
        print(f"{'='*50}")
        price_data = get_stock_price(sym)
        print(json.dumps(price_data, indent=2))

        print(f"\n  Stock History — {sym} (7d)")
        print(f"{'─'*50}")
        history_data = get_stock_history(sym, period="7d")
        # Print just the summary + last 3 rows for brevity
        summary = {k: v for k, v in history_data.items() if k != "history"}
        print(json.dumps(summary, indent=2))
        print("  Last 3 entries:")
        print(json.dumps(history_data.get("history", [])[-3:], indent=2))
