"""
sentiment_analysis.py — Financial Sentiment Analysis Module

Engines used:
    1. NLTK VADER  — rule-based, tuned for short social/news text
    2. TextBlob    — pattern-based polarity scoring

Both scores are averaged into a single combined_score with a label.
VADER is weighted higher (0.65) because it outperforms on financial headlines.

Usage:
    from backend.sentiment_analysis import analyze_sentiment
    result = analyze_sentiment("Tesla stock surges after record profits")
"""

import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from typing import Literal

# ─── Download VADER lexicon silently ─────────────────────────────────────────
nltk.download("vader_lexicon", quiet=True)

# ─── Sentiment label thresholds ───────────────────────────────────────────────
# Combined score is in range [-1.0, +1.0]
POSITIVE_THRESHOLD =  0.05
NEGATIVE_THRESHOLD = -0.05

# Engine weights (must sum to 1.0)
VADER_WEIGHT     = 0.65
TEXTBLOB_WEIGHT  = 0.35

# ─── Optional: finance-domain boosters ───────────────────────────────────────
# Words that VADER may underweight in financial context.
# Applied as a small fixed nudge before final scoring.
POSITIVE_BOOSTERS = {
    "surge", "rally", "breakout", "soar", "beat", "record",
    "profit", "gain", "upgrade", "outperform", "dividend", "recovery",
}
NEGATIVE_BOOSTERS = {
    "crash", "plunge", "miss", "downgrade", "loss", "slump",
    "tumble", "decline", "fall", "correction", "bearish", "default",
}

BOOST_VALUE = 0.07   # nudge per matched booster word


def _label(score: float) -> Literal["positive", "negative", "neutral"]:
    """Map a numeric score to a sentiment label."""
    if score >= POSITIVE_THRESHOLD:
        return "positive"
    if score <= NEGATIVE_THRESHOLD:
        return "negative"
    return "neutral"


def _finance_boost(text: str) -> float:
    """
    Return a small domain-specific nudge based on finance signal words
    to help resolve borderline neutral scores.
    """
    words = set(text.lower().split())
    pos_hits = len(words & POSITIVE_BOOSTERS)
    neg_hits = len(words & NEGATIVE_BOOSTERS)
    return (pos_hits - neg_hits) * BOOST_VALUE


def analyze_sentiment(text: str) -> dict:
    """
    Analyse the sentiment of a financial text string.

    Args:
        text (str): A news headline, tweet, or user message.

    Returns:
        dict: {
            "sentiment"      : "positive" | "negative" | "neutral",
            "score"          : float,   # combined score in [-1.0, +1.0]
            "vader_score"    : float,   # VADER compound score
            "textblob_score" : float,   # TextBlob polarity score
            "confidence"     : str,     # "high" | "medium" | "low"
            "input"          : str      # original text (for traceability)
        }
    """
    if not text or not text.strip():
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "vader_score": 0.0,
            "textblob_score": 0.0,
            "confidence": "low",
            "input": text,
        }

    # ── Engine 1: VADER ───────────────────────────────────────────────────────
    sia = SentimentIntensityAnalyzer()
    vader_compound = sia.polarity_scores(text)["compound"]  # [-1, +1]

    # ── Engine 2: TextBlob ────────────────────────────────────────────────────
    blob = TextBlob(text)
    textblob_polarity = blob.sentiment.polarity               # [-1, +1]

    # ── Combine ───────────────────────────────────────────────────────────────
    combined = (
        VADER_WEIGHT    * vader_compound +
        TEXTBLOB_WEIGHT * textblob_polarity +
        _finance_boost(text)
    )
    combined = max(-1.0, min(1.0, combined))   # clamp to [-1, 1]

    # ── Confidence: how strongly do both engines agree? ───────────────────────
    agreement = abs(vader_compound - textblob_polarity)
    strength  = abs(combined)
    if strength >= 0.4 and agreement <= 0.4:
        confidence = "high"
    elif strength >= 0.15 or agreement <= 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "sentiment"      : _label(combined),
        "score"          : round(combined, 4),
        "vader_score"    : round(vader_compound, 4),
        "textblob_score" : round(textblob_polarity, 4),
        "confidence"     : confidence,
        "input"          : text,
    }


def analyze_sentiment_batch(texts: list[str]) -> list[dict]:
    """
    Run analyze_sentiment() over a list of texts.

    Args:
        texts (list[str]): List of financial news strings.

    Returns:
        list[dict]: Sentiment result for each input in order.
    """
    return [analyze_sentiment(t) for t in texts]


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        # Clearly positive
        "Tesla stock surges after record profits",
        "Apple shares rally as investors cheer strong revenue beat",
        "Amazon posts best quarter ever, stock soars 12%",
        # Clearly negative
        "Bitcoin crashes below $30,000 as market sentiment turns bearish",
        "Google stock plunges on regulatory concerns and revenue miss",
        "Fed rate hike triggers stock market correction and heavy losses",
        # Borderline / Neutral
        "Federal Reserve holds rates steady; analysts remain cautious",
        "Markets close flat amid mixed earnings season results",
        "Analysts are divided on whether the next move will be up or down",
    ]

    ICONS = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}

    print("\n" + "═" * 65)
    print("  📊  Financial Sentiment Analysis — Demo Results")
    print("═" * 65)

    for sentence in test_cases:
        r = analyze_sentiment(sentence)
        icon = ICONS[r["sentiment"]]
        print(f"\n{icon}  {r['input']}")
        print(f"   Sentiment  : {r['sentiment'].upper():10}  (confidence: {r['confidence']})")
        print(f"   Score      : {r['score']:+.4f}  "
              f"[VADER: {r['vader_score']:+.4f} | TextBlob: {r['textblob_score']:+.4f}]")
        print(f"   JSON output:")
        out = {k: v for k, v in r.items() if k != "input"}
        print(f"   {json.dumps(out)}")
