"""
evaluate.py — Reproducible evaluation of FinBot's components.

Computes (offline, no network needed):
  1. Intent classification  — 5-fold stratified CV on TRAINING_DATA + a
                              hand-written held-out test set
  2. Entity (ticker) extraction — exact-match accuracy + precision/recall/F1
  3. Trend detection        — walk-forward directional accuracy of the SMA
                              signal on data/*_history.csv vs. a naive baseline

Results are written to data/evaluation.json, which GET /metrics serves.

Run:  python backend/evaluate.py
"""

import json
import os
import sys
import datetime
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from chatbot import TRAINING_DATA, IntentClassifier, extract_ticker
from market_analyzer import detect_trend

ROOT      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_DIR  = os.path.join(ROOT, "data")
OUT_PATH  = os.path.join(DATA_DIR, "evaluation.json")

# ─── Held-out intent test set (written independently of the training data) ────
HELD_OUT_INTENT = [
    # stock_price
    ("how much is Netflix trading at right now", "stock_price"),
    ("current quote for Microsoft", "stock_price"),
    ("what's the share price of Google today", "stock_price"),
    ("tell me the live price of Amazon", "stock_price"),
    ("Tesla stock value at the moment", "stock_price"),
    ("what is Meta trading for", "stock_price"),
    ("give me the latest price of Infosys", "stock_price"),
    ("how much does one Nvidia share cost", "stock_price"),
    ("show Reliance stock price", "stock_price"),
    ("price of Bitcoin now", "stock_price"),
    ("what did Apple open at today", "stock_price"),
    ("Wipro share rate", "stock_price"),
    # market_trend
    ("is Tesla in an uptrend", "market_trend"),
    ("what is the moving average trend for Microsoft", "market_trend"),
    ("is Amazon bullish or bearish", "market_trend"),
    ("how has Google been performing lately", "market_trend"),
    ("show me the SMA and EMA for Apple", "market_trend"),
    ("is Nvidia trending up or down", "market_trend"),
    ("market direction of Netflix stock", "market_trend"),
    ("technical trend analysis of Meta", "market_trend"),
    ("is the momentum positive for Infosys", "market_trend"),
    ("Tesla price movement over the last few weeks", "market_trend"),
    ("is Ethereum in a downtrend", "market_trend"),
    ("trend analysis for TCS", "market_trend"),
    # news_sentiment
    ("any recent headlines about Tesla", "news_sentiment"),
    ("what is the news sentiment around Apple", "news_sentiment"),
    ("are people positive about Nvidia lately", "news_sentiment"),
    ("show me news on Amazon", "news_sentiment"),
    ("what is the media saying about Microsoft", "news_sentiment"),
    ("latest articles about Google and how they read", "news_sentiment"),
    ("is the news bad for Meta", "news_sentiment"),
    ("market sentiment for Netflix", "news_sentiment"),
    ("sentiment of recent Reliance news", "news_sentiment"),
    ("what are analysts and journalists saying about Bitcoin", "news_sentiment"),
    ("any good news for Tesla this week", "news_sentiment"),
    ("news headlines for Infosys", "news_sentiment"),
    # recommendation
    ("should I buy Tesla", "recommendation"),
    ("is Apple a good investment right now", "recommendation"),
    ("would you advise selling Amazon", "recommendation"),
    ("is it a good time to invest in Nvidia", "recommendation"),
    ("buy or sell Microsoft", "recommendation"),
    ("should I hold my Google shares", "recommendation"),
    ("is Netflix worth buying", "recommendation"),
    ("give me a recommendation for Meta", "recommendation"),
    ("is Bitcoin a safe investment", "recommendation"),
    ("should I put money into Reliance", "recommendation"),
    ("do you recommend buying Infosys", "recommendation"),
    ("is TCS a buy right now", "recommendation"),
]

# ─── Entity extraction test set: (query, gold ticker or None) ─────────────────
ENTITY_TESTS = [
    ("What is Tesla stock price?", "TSLA"),
    ("how is Apple doing", "AAPL"),
    ("Should I buy MSFT?", "MSFT"),
    ("latest news about Nvidia", "NVDA"),
    ("price of Amazon shares", "AMZN"),
    ("is Google bullish", "GOOGL"),
    ("Netflix trend", "NFLX"),
    ("how is Meta performing", "META"),
    ("tell me about Reliance", "RELIANCE.NS"),
    ("Infosys stock price", "INFY.NS"),
    ("is Bitcoin a good buy", "BTC-USD"),
    ("Ethereum trend", "ETH-USD"),
    ("TCS share price", "TCS.NS"),
    ("Wipro news sentiment", "WIPRO.NS"),
    ("tata motors stock", "TMPV.NS"),
    ("what's the TSLA price", "TSLA"),
    ("is AAPL a buy", "AAPL"),
    ("NVDA trend", "NVDA"),
    ("how is HDFC doing", "HDFCBANK.NS"),
    ("ICICI bank price", "ICICIBANK.NS"),
    ("hello", None),
    ("what can you do", None),
    ("how are you today", None),
    ("tell me a joke", None),
    ("what is the weather", None),
]


# ─── 1. Intent ────────────────────────────────────────────────────────────────
def eval_intent() -> dict:
    texts, labels = zip(*TRAINING_DATA)

    # Cross-validation with a fresh pipeline (same hyper-parameters as the bot)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 3), lowercase=True, min_df=1)),
        ("clf",   MultinomialNB(alpha=0.05)),
    ])
    cv   = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pred = cross_val_predict(pipe, texts, labels, cv=cv)
    cv_acc = accuracy_score(labels, pred)
    p, r, f, _ = precision_recall_fscore_support(labels, pred, average="macro", zero_division=0)

    # Held-out set (drop anything that also appears in training data)
    train_set = {t.lower() for t in texts}
    held = [(t, l) for t, l in HELD_OUT_INTENT if t.lower() not in train_set]
    # Fit in memory only — do not overwrite models/intent_classifier.pkl
    clf = IntentClassifier()
    enc = clf.label_encoder.fit_transform(labels)
    clf.pipeline.fit(texts, enc)
    clf._trained = True
    ht, hl = zip(*held)
    hp = [clf.predict(t)[0] for t in ht]
    h_acc = accuracy_score(hl, hp)
    hp_, hr_, hf_, _ = precision_recall_fscore_support(hl, hp, average="macro", zero_division=0)

    return {
        "training_size": len(TRAINING_DATA),
        "cross_validation_5fold": {
            "accuracy": round(cv_acc * 100, 1), "precision": round(p * 100, 1),
            "recall": round(r * 100, 1), "f1": round(f * 100, 1),
        },
        "held_out": {
            "n": len(held),
            "accuracy": round(h_acc * 100, 1), "precision": round(hp_ * 100, 1),
            "recall": round(hr_ * 100, 1), "f1": round(hf_ * 100, 1),
            "errors": [{"text": t, "expected": l, "got": g}
                       for (t, l), g in zip(held, hp) if l != g],
        },
    }


# ─── 2. Entity ────────────────────────────────────────────────────────────────
def eval_entity() -> dict:
    tp = fp = fn = correct = 0
    errors = []
    for text, gold in ENTITY_TESTS:
        got = extract_ticker(text)
        if got == gold:
            correct += 1
            if gold is not None:
                tp += 1
        else:
            errors.append({"text": text, "expected": gold, "got": got})
            if got is not None:
                fp += 1
            if gold is not None:
                fn += 1
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec  = tp / (tp + fn) if tp + fn else 0.0
    f1   = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "n": len(ENTITY_TESTS),
        "accuracy":  round(correct / len(ENTITY_TESTS) * 100, 1),
        "precision": round(prec * 100, 1),
        "recall":    round(rec * 100, 1),
        "f1":        round(f1 * 100, 1),
        "errors":    errors,
    }


# ─── 3. Trend (walk-forward) ──────────────────────────────────────────────────
def eval_trend(window: int = 14, horizon: int = 5) -> dict:
    """
    At each day t, the SMA signal (bullish/bearish) is compared with the sign of
    the return over the next `horizon` trading days. Neutral signals are skipped.
    Baseline: always predict 'up'.
    """
    hits = total = base_hits = 0
    per_symbol = {}
    for fn_ in sorted(os.listdir(DATA_DIR)):
        if not fn_.endswith("_history.csv"):
            continue
        sym    = fn_.replace("_history.csv", "")
        closes = pd.read_csv(os.path.join(DATA_DIR, fn_))["Close"].astype(float).tolist()
        h = t = b = 0
        for i in range(window, len(closes) - horizon):
            sig = detect_trend(closes[: i + 1], window=window)["trend"]
            if sig == "neutral":
                continue
            up = closes[i + horizon] > closes[i]
            t += 1
            h += (sig == "bullish") == up
            b += up
        per_symbol[sym] = {"signals": t, "accuracy": round(h / t * 100, 1) if t else None,
                           "always_up_baseline": round(b / t * 100, 1) if t else None}
        hits, total, base_hits = hits + h, total + t, base_hits + b
    return {
        "method": f"SMA-{window} vs price, dead-band 0.5%, {horizon}-day forward direction",
        "signals": total,
        "directional_accuracy": round(hits / total * 100, 1) if total else None,
        "always_up_baseline":   round(base_hits / total * 100, 1) if total else None,
        "per_symbol": per_symbol,
    }


def main() -> None:
    result = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "intent":  eval_intent(),
        "entity":  eval_entity(),
        "trend":   eval_trend(),
        "not_measured": [
            "response_relevance and conversation_success_rate need human-rated "
            "conversations; avg response time needs a live server.",
        ],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result, indent=2))
    print(f"\nSaved → {os.path.abspath(OUT_PATH)}")


if __name__ == "__main__":
    main()
