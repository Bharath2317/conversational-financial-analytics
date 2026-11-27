"""
price_predictor.py — ML Stock Price Prediction using scikit-learn

Algorithm:
  • Fetches 2 years of OHLCV history from yfinance
  • Engineers 15+ features (lag prices, rolling MAs, returns, volatility, calendar)
  • Trains a Random Forest Regressor to predict next-day closing price
  • Saves trained model + scaler to models/{symbol}_predictor.pkl
  • Loads cached model on repeat calls (instant prediction, no retraining)

No external data files needed — yfinance fetches everything live.
"""

import os
import json
import warnings
import datetime
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
import yfinance as yf

from sklearn.ensemble         import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model     import LinearRegression, Ridge
from sklearn.preprocessing    import StandardScaler
from sklearn.model_selection  import train_test_split
from sklearn.metrics          import mean_absolute_error, mean_squared_error, r2_score


# ─── Paths ─────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")
DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR,   exist_ok=True)


# ─── Feature Engineering ───────────────────────────────────────────────────────
def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create technical indicator features from raw OHLCV DataFrame."""
    d = df.copy()

    # Lag close prices
    for lag in [1, 2, 3, 5, 10]:
        d[f"close_lag_{lag}"] = d["Close"].shift(lag)

    # Rolling statistics
    for window in [5, 10, 20, 50]:
        d[f"sma_{window}"]     = d["Close"].rolling(window).mean()
        d[f"std_{window}"]     = d["Close"].rolling(window).std()
        d[f"high_roll_{window}"]= d["High"].rolling(window).max()
        d[f"low_roll_{window}"] = d["Low"].rolling(window).min()

    # Returns
    d["daily_return"]   = d["Close"].pct_change()
    d["return_5d"]      = d["Close"].pct_change(5)
    d["return_10d"]     = d["Close"].pct_change(10)

    # Volatility
    d["volatility_5d"]  = d["daily_return"].rolling(5).std()
    d["volatility_20d"] = d["daily_return"].rolling(20).std()

    # Price ratios
    d["hl_ratio"]       = (d["High"] - d["Low"]) / d["Close"]
    d["co_ratio"]       = (d["Close"] - d["Open"]) / d["Open"]

    # Volume features
    d["volume_ma_10"]   = d["Volume"].rolling(10).mean()
    d["volume_ratio"]   = d["Volume"] / (d["volume_ma_10"] + 1)

    # Calendar features
    d["day_of_week"]    = d.index.dayofweek
    d["month"]          = d.index.month
    d["quarter"]        = d.index.quarter

    # Target: next day's closing price
    d["target"] = d["Close"].shift(-1)

    return d.dropna()


# ─── Train & Save ──────────────────────────────────────────────────────────────
def train_model(symbol: str, period: str = "2y") -> dict:
    """
    Fetch historical data, engineer features, train Random Forest,
    evaluate, and save model + scaler to disk.

    Args:
        symbol (str): Ticker, e.g. "AAPL"
        period (str): yfinance period (default "2y")

    Returns:
        dict: Training report with metrics and model path
    """
    print(f"  ⏳ Fetching {period} history for {symbol}…")
    ticker = yf.Ticker(symbol)
    df     = ticker.history(period=period)

    if df.empty or len(df) < 60:
        return {"error": f"Not enough data to train for {symbol}"}

    # Save raw data to data/
    raw_path = os.path.join(DATA_DIR, f"{symbol}_history.csv")
    df.to_csv(raw_path)
    print(f"  💾 Raw data saved → {raw_path}  ({len(df)} rows)")

    # Feature engineering
    df_feat = _build_features(df)

    feature_cols = [c for c in df_feat.columns if c not in ("target", "Dividends", "Stock Splits")]
    X = df_feat[feature_cols].values
    y = df_feat["target"].values

    # Train / test split (80/20, time-ordered)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # Train models and pick best
    models = {
        "RandomForest"    : RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "Ridge"           : Ridge(alpha=1.0),
    }

    best_model, best_r2, best_name = None, -999, ""
    results = {}

    for name, model in models.items():
        model.fit(X_train_s, y_train)
        preds  = model.predict(X_test_s)
        mae    = mean_absolute_error(y_test, preds)
        rmse   = np.sqrt(mean_squared_error(y_test, preds))
        r2     = r2_score(y_test, preds)
        results[name] = {"mae": round(mae,4), "rmse": round(rmse,4), "r2": round(r2,4)}
        print(f"  📊 {name:20s}: MAE={mae:.2f}  RMSE={rmse:.2f}  R²={r2:.4f}")
        if r2 > best_r2:
            best_r2, best_model, best_name = r2, model, name

    # Save best model + scaler + metadata
    model_path = os.path.join(MODELS_DIR, f"{symbol}_predictor.pkl")
    meta_path  = os.path.join(MODELS_DIR, f"{symbol}_meta.json")

    joblib.dump({"model": best_model, "scaler": scaler, "features": feature_cols}, model_path)

    last_price = float(df["Close"].iloc[-1])
    meta = {
        "symbol"      : symbol,
        "best_model"  : best_name,
        "r2_score"    : round(best_r2, 4),
        "trained_on"  : datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data_rows"   : len(df_feat),
        "period"      : period,
        "last_price"  : last_price,
        "all_results" : results,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  ✅ Best: {best_name} (R²={best_r2:.4f})")
    print(f"  💾 Model saved → {model_path}")

    return meta


# ─── Predict ──────────────────────────────────────────────────────────────────
def predict_next_price(symbol: str) -> dict:
    """
    Predict the next day's closing price using the saved model.
    Auto-trains if no saved model exists for the symbol.

    Args:
        symbol (str): Ticker, e.g. "AAPL"

    Returns:
        dict: {
            "symbol"        : str,
            "current_price" : float,
            "predicted_price": float,
            "predicted_change": float,
            "predicted_change_pct": float,
            "direction"     : "up" | "down" | "flat",
            "model_used"    : str,
            "r2_score"      : float,
            "confidence"    : str
        }
    """
    model_path = os.path.join(MODELS_DIR, f"{symbol}_predictor.pkl")
    meta_path  = os.path.join(MODELS_DIR, f"{symbol}_meta.json")

    # Auto-train if model doesn't exist
    if not os.path.exists(model_path):
        print(f"  🔄 No saved model for {symbol}. Training now…")
        train_result = train_model(symbol)
        if "error" in train_result:
            return {"error": train_result["error"], "symbol": symbol}

    # Load model
    bundle = joblib.load(model_path)
    model, scaler, feature_cols = bundle["model"], bundle["scaler"], bundle["features"]

    # Load meta
    with open(meta_path) as f:
        meta = json.load(f)

    # Fetch latest data for prediction
    df_raw  = yf.Ticker(symbol).history(period="3mo")
    if df_raw.empty:
        return {"error": "Could not fetch recent data.", "symbol": symbol}

    df_feat = _build_features(df_raw)
    if df_feat.empty:
        return {"error": "Could not build features.", "symbol": symbol}

    # Use the most recent row as input
    avail_cols = [c for c in feature_cols if c in df_feat.columns]
    last_row   = df_feat[avail_cols].iloc[-1].values.reshape(1, -1)

    # Align columns (fill missing with 0)
    if len(avail_cols) < len(feature_cols):
        full_row = np.zeros((1, len(feature_cols)))
        for i, col in enumerate(feature_cols):
            if col in avail_cols:
                idx = avail_cols.index(col)
                full_row[0, i] = last_row[0, idx]
        last_row = full_row

    last_row_s     = scaler.transform(last_row)
    predicted      = float(model.predict(last_row_s)[0])
    current_price  = float(df_raw["Close"].iloc[-1])
    change         = round(predicted - current_price, 4)
    change_pct     = round((change / current_price) * 100, 4)

    direction = "up" if change > 0.5 else "down" if change < -0.5 else "flat"
    r2 = meta.get("r2_score", 0)
    confidence = "high" if r2 >= 0.85 else "medium" if r2 >= 0.65 else "low"

    return {
        "symbol"              : symbol.upper(),
        "current_price"       : round(current_price, 4),
        "predicted_price"     : round(predicted, 4),
        "predicted_change"    : change,
        "predicted_change_pct": change_pct,
        "direction"           : direction,
        "model_used"          : meta.get("best_model", "Unknown"),
        "r2_score"            : r2,
        "confidence"          : confidence,
        "trained_on"          : meta.get("trained_on", ""),
    }


# ─── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SYMBOLS = ["AAPL", "TSLA", "MSFT"]

    print("\n" + "═"*65)
    print("  🧠  Price Predictor — Training & Prediction Demo")
    print("═"*65)

    for sym in SYMBOLS:
        print(f"\n{'─'*65}")
        print(f"  Training model for {sym}…")
        train_model(sym)
        print(f"\n  Predicting next price for {sym}…")
        result = predict_next_price(sym)
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            arrow = "⬆" if result["direction"] == "up" else "⬇" if result["direction"] == "down" else "➡"
            print(f"  {arrow} Current  : ${result['current_price']}")
            print(f"  {arrow} Predicted: ${result['predicted_price']}  ({result['predicted_change_pct']:+.2f}%)")
            print(f"  Model    : {result['model_used']}  |  R²={result['r2_score']}  |  Confidence: {result['confidence']}")
