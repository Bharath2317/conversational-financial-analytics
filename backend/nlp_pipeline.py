"""
nlp_pipeline.py — Financial Text NLP Pipeline

Features:
    1. Text cleaning   — lowercase, strip punctuation, remove stopwords
    2. Tokenization    — split into meaningful word tokens
    3. Lemmatization   — reduce words to their base (root) form
    4. NER             — extract company / organisation names via spaCy
    5. Finance keywords — detect pre-defined bullish/bearish signal words
"""

import re
import string
import json
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import Optional

# ─── One-time NLTK downloads (silent) ────────────────────────────────────────
for _pkg in ("stopwords", "wordnet", "punkt", "punkt_tab"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

# ─── Finance signal keywords ─────────────────────────────────────────────────
FINANCE_KEYWORDS: set[str] = {
    # Bullish signals
    "breakout", "spike", "surge", "rally", "bullish", "uptrend",
    "bounce", "soar", "gain", "buy", "overbought", "recovery",
    "outperform", "upgrade", "beat",
    # Bearish signals
    "fall", "drop", "crash", "bearish", "downtrend", "decline",
    "plunge", "sell", "oversold", "downgrade", "miss", "correction",
    "slump", "tumble", "loss",
    # Neutral but notable
    "earnings", "revenue", "guidance", "forecast", "dividend",
    "merger", "acquisition", "ipo", "split",
}

# ─── Load spaCy model (with graceful fallback) ────────────────────────────────
_NLP_MODEL: Optional[spacy.language.Language] = None

def _load_spacy() -> spacy.language.Language:
    """Load spaCy en_core_web_sm; fall back to blank model if unavailable."""
    global _NLP_MODEL
    if _NLP_MODEL is not None:
        return _NLP_MODEL
    try:
        _NLP_MODEL = spacy.load("en_core_web_sm")
    except OSError:
        print(
            "[nlp_pipeline] WARNING: 'en_core_web_sm' not found. "
            "Company NER will be skipped. Run:\n"
            "  python -m spacy download en_core_web_sm"
        )
        _NLP_MODEL = spacy.blank("en")
    return _NLP_MODEL


# ─── Core pipeline ────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Lowercase, strip punctuation and extra whitespace."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove common English stopwords."""
    stop_words = set(stopwords.words("english"))
    return [t for t in tokens if t not in stop_words]


def _lemmatize(tokens: list[str]) -> list[str]:
    """Reduce each token to its base lemma form."""
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(t) for t in tokens]


def _extract_companies(text: str) -> list[str]:
    """
    Use spaCy Named Entity Recognition to extract ORG / PRODUCT entities,
    which typically capture company names like 'Tesla', 'Apple', 'Amazon'.
    """
    nlp = _load_spacy()
    # Use the original (uncleaned) text for better NER accuracy
    doc = nlp(text)
    companies = []
    seen = set()
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "GPE"):
            name = ent.text.strip()
            if name.lower() not in seen:
                seen.add(name.lower())
                companies.append(name)
    return companies


def _detect_keywords(tokens: list[str]) -> list[str]:
    """
    Match cleaned/lemmatized tokens against the finance keyword list.
    Returns matched keywords in order of first appearance (deduplicated).
    """
    found = []
    seen = set()
    for token in tokens:
        if token in FINANCE_KEYWORDS and token not in seen:
            seen.add(token)
            found.append(token)
    return found


# ─── Public API ───────────────────────────────────────────────────────────────

def analyze(text: str) -> dict:
    """
    Run the full NLP pipeline on a piece of financial text.

    Args:
        text (str): Raw input, e.g. a news headline or user message.

    Returns:
        dict: {
            "input":     str,           # original text
            "tokens":    list[str],     # cleaned, lemmatized, no stopwords
            "companies": list[str],     # org/company names from NER
            "keywords":  list[str]      # matched finance signal keywords
        }
    """
    if not text or not text.strip():
        return {"input": text, "tokens": [], "companies": [], "keywords": []}

    # Step 1 — Company extraction (before cleaning for better NER)
    companies = _extract_companies(text)

    # Step 2 — Clean text
    cleaned = _clean_text(text)

    # Step 3 — Tokenize
    raw_tokens = cleaned.split()

    # Step 4 — Remove stopwords
    filtered_tokens = _remove_stopwords(raw_tokens)

    # Step 5 — Lemmatize
    lemmatized_tokens = _lemmatize(filtered_tokens)

    # Step 6 — Detect finance keywords (on lemmatized tokens)
    keywords = _detect_keywords(lemmatized_tokens)

    return {
        "input": text,
        "tokens": lemmatized_tokens,
        "companies": companies,
        "keywords": keywords,
    }


# ─── Batch analysis ───────────────────────────────────────────────────────────

def analyze_batch(texts: list[str]) -> list[dict]:
    """Run analyze() over a list of texts, returning results in the same order."""
    return [analyze(t) for t in texts]


# ─── Demo if run directly ────────────────────────────────────────────────────

if __name__ == "__main__":
    test_sentences = [
        "Tesla stock shows huge spike after earnings report",
        "Apple shares rally as investors cheer record revenue beat",
        "Bitcoin crash wipes out billions; analysts warn of bearish downtrend",
        "Amazon announces acquisition of a major logistics startup",
        "Google stock drops amid regulatory concerns and revenue miss",
        "Bullish breakout seen in Microsoft after strong earnings guidance",
    ]

    print("\n" + "═" * 60)
    print("  🔍  Financial NLP Pipeline — Demo Results")
    print("═" * 60)

    for sentence in test_sentences:
        result = analyze(sentence)
        print(f"\n📰 Input   : {result['input']}")
        print(f"🔤 Tokens  : {result['tokens']}")
        print(f"🏢 Companies: {result['companies']}")
        print(f"📊 Keywords: {result['keywords']}")
        print(f"── JSON ──")
        clean_result = {k: v for k, v in result.items() if k != "input"}
        print(json.dumps(clean_result, indent=2))
