"""
alert_system.py — Real-time Financial Alert Engine

Triggers:
  • Negative sentiment detected on any stock query
  • Price change exceeds ±5% vs previous close
  • Specific bearish keywords detected in user input

Persists all alerts to data/alerts.json (survives restarts).
Optional: extend send_alert() to email / Slack / webhook.
"""

import os
import json
import datetime
from typing import Literal

# ─── Persistent storage path ──────────────────────────────────────────────────
DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
ALERTS_FILE = os.path.join(DATA_DIR, "alerts.json")
os.makedirs(DATA_DIR, exist_ok=True)

def _load_alerts() -> list:
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_alerts(store: list) -> None:
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(store, f, indent=2)
    except Exception:
        pass

# ─── Alert store (in-memory + persisted to JSON) ────────────────────────────
_alert_store: list[dict] = _load_alerts()

AlertLevel = Literal["INFO", "WARNING", "CRITICAL"]


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_alert(
    level: AlertLevel,
    ticker: str,
    message: str,
    extra: dict | None = None,
) -> dict:
    """
    Create an alert, log it to console, store it in memory.

    Args:
        level   : "INFO" | "WARNING" | "CRITICAL"
        ticker  : Stock symbol, e.g. "TSLA"
        message : Alert description
        extra   : Optional dict with supporting data

    Returns:
        dict: The created alert object
    """
    icons = {"INFO": "ℹ️ ", "WARNING": "⚠️ ", "CRITICAL": "🚨"}
    alert = {
        "id"       : len(_alert_store) + 1,
        "level"    : level,
        "ticker"   : ticker,
        "message"  : message,
        "timestamp": _now(),
        "extra"    : extra or {},
    }
    _alert_store.append(alert)
    _save_alerts(_alert_store)   # persist to disk

    # ── Console output
    border = "═" * 60 if level == "CRITICAL" else "─" * 60
    print(f"\n{border}")
    print(f"  {icons[level]} ALERT [{level}] — {_now()}")
    print(f"  Ticker  : {ticker}")
    print(f"  Message : {message}")
    if extra:
        for k, v in extra.items():
            print(f"  {k:<10}: {v}")
    print(f"{border}")

    # ── Optional: email hook (extend here)
    # _send_email(alert)

    return alert


def check_price_alert(ticker: str, price_data: dict) -> list[dict]:
    """
    Fire alerts based on price movement.

    Rules:
      |change_pct| > 10%  → CRITICAL (huge spike/crash)
      |change_pct| > 5%   → WARNING  (significant move)
    """
    alerts = []
    change_pct = float(price_data.get("change_pct", 0))
    price      = price_data.get("price", 0)
    change     = price_data.get("change", 0)

    if abs(change_pct) > 10:
        direction = "spike" if change_pct > 0 else "crash"
        alerts.append(send_alert(
            level   = "CRITICAL",
            ticker  = ticker,
            message = f"Alert: {ticker} stock showing HUGE {direction} of {change_pct:+.2f}%!",
            extra   = {"price": price, "change": change, "change_pct": f"{change_pct:+.2f}%"},
        ))
    elif abs(change_pct) > 5:
        direction = "surge" if change_pct > 0 else "drop"
        alerts.append(send_alert(
            level   = "WARNING",
            ticker  = ticker,
            message = f"Alert: {ticker} stock {direction} detected — {change_pct:+.2f}% move.",
            extra   = {"price": price, "change": change, "change_pct": f"{change_pct:+.2f}%"},
        ))
    return alerts


def check_sentiment_alert(ticker: str, sentiment_data: dict) -> list[dict]:
    """
    Fire alerts when sentiment is strongly negative.

    Rules:
      score < -0.5              → CRITICAL (very negative)
      score < -0.05 (negative)  → WARNING
    """
    alerts = []
    score     = float(sentiment_data.get("score", 0))
    sentiment = sentiment_data.get("sentiment", "neutral")
    confidence = sentiment_data.get("confidence", "low")

    if sentiment == "negative" and score < -0.5:
        alerts.append(send_alert(
            level   = "CRITICAL",
            ticker  = ticker,
            message = f"Alert: {ticker} showing STRONG negative sentiment (score: {score:+.4f}).",
            extra   = {"score": score, "confidence": confidence},
        ))
    elif sentiment == "negative":
        alerts.append(send_alert(
            level   = "WARNING",
            ticker  = ticker,
            message = f"Alert: {ticker} stock showing negative market sentiment.",
            extra   = {"score": score, "confidence": confidence},
        ))
    return alerts


def check_trend_alert(ticker: str, trend_report: dict) -> list[dict]:
    """Fire alerts on extreme bearish deviation from moving average."""
    alerts = []
    sma = trend_report.get("sma_trend", {})
    dev = float(sma.get("deviation_pct", 0))

    if dev < -8:
        alerts.append(send_alert(
            level   = "CRITICAL",
            ticker  = ticker,
            message = f"Alert: {ticker} is {abs(dev):.1f}% BELOW its 14-day SMA — extreme bearish signal.",
            extra   = {"deviation_pct": f"{dev:+.2f}%", "sma": sma.get("moving_average")},
        ))
    elif dev < -5:
        alerts.append(send_alert(
            level   = "WARNING",
            ticker  = ticker,
            message = f"Alert: {ticker} is {abs(dev):.1f}% below 14-day SMA — bearish trend detected.",
            extra   = {"deviation_pct": f"{dev:+.2f}%", "sma": sma.get("moving_average")},
        ))
    return alerts


def run_all_checks(ticker: str, price_data: dict, sentiment_data: dict, trend_report: dict) -> list[dict]:
    """Run all alert checks and return list of triggered alerts."""
    triggered = []
    if "error" not in price_data:
        triggered.extend(check_price_alert(ticker, price_data))
    if "error" not in sentiment_data:
        triggered.extend(check_sentiment_alert(ticker, sentiment_data))
    if "error" not in trend_report:
        triggered.extend(check_trend_alert(ticker, trend_report))
    return triggered


def get_all_alerts() -> list[dict]:
    """Return all stored alerts (most recent first)."""
    return list(reversed(_alert_store))


def get_alerts_by_ticker(ticker: str) -> list[dict]:
    return [a for a in reversed(_alert_store) if a["ticker"].upper() == ticker.upper()]


def clear_alerts() -> None:
    _alert_store.clear()
    _save_alerts(_alert_store)
