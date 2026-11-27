"""
chatbot.py — Financial Chatbot with Intent Detection & Entity Extraction

Intent Classes:
    1) stock_price     — "What is Tesla stock price?"
    2) market_trend    — "What is the trend of Apple?"
    3) news_sentiment  — "Latest news sentiment about Nvidia?"
    4) recommendation  — "Should I buy TATA stock?"
    5) unknown         — Fallback for unrecognised queries

Pipeline:
    Query → Intent Classifier (sklearn TF-IDF + Naive Bayes)
           → Entity Extractor (spaCy NER + ticker map)
           → Module Dispatcher (stock_api / market_analyzer / sentiment_analysis / news_fetcher / price_predictor)
           → Natural Language Response Builder

Model saved to models/intent_classifier.pkl — only retrains if new data.
"""

import json
import os
import re
import warnings
warnings.filterwarnings("ignore")
import joblib

# scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Our own modules
from stock_api          import get_stock_price, get_stock_history
from sentiment_analysis import analyze_sentiment
from market_analyzer    import detect_trend, full_analysis
from nlp_pipeline       import analyze as nlp_analyze
from news_fetcher       import fetch_news
from price_predictor    import predict_next_price

# Paths
MODELS_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "intent_classifier.pkl")
os.makedirs(MODELS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TRAINING DATA — labelled sentences for intent classification
# ══════════════════════════════════════════════════════════════════════════════

TRAINING_DATA: list[tuple[str, str]] = [
    # ── stock_price (50 examples) ──────────────────────────────────────────
    ("what is the stock price of Tesla",            "stock_price"),
    ("show me Apple stock price",                   "stock_price"),
    ("current price of Microsoft",                  "stock_price"),
    ("Tesla price today",                           "stock_price"),
    ("how much is Amazon stock",                    "stock_price"),
    ("give me the price of Google shares",          "stock_price"),
    ("latest price for NVDA",                       "stock_price"),
    ("what is AAPL trading at",                     "stock_price"),
    ("tell me the share price of Reliance",         "stock_price"),
    ("price of TSLA right now",                     "stock_price"),
    ("stock price of TATA",                         "stock_price"),
    ("current share value of Infosys",              "stock_price"),
    ("how much does Google stock cost",             "stock_price"),
    ("what is the current price of Netflix",        "stock_price"),
    ("check Amazon share price",                    "stock_price"),
    ("get me MSFT stock price",                     "stock_price"),
    ("what is Meta trading at today",               "stock_price"),
    ("how much is Nvidia stock worth",              "stock_price"),
    ("price check on AAPL",                         "stock_price"),
    ("what is TSLA stock at right now",             "stock_price"),
    ("quote for Apple shares",                      "stock_price"),
    ("current market price of Tesla",               "stock_price"),
    ("share price for GOOGL",                       "stock_price"),
    ("how much is Intel worth today",               "stock_price"),
    ("get stock quote AMZN",                        "stock_price"),
    ("what is Bitcoin trading at",                  "stock_price"),
    ("Ethereum current price",                      "stock_price"),
    ("check TCS stock price",                       "stock_price"),
    ("current value of Wipro shares",               "stock_price"),
    ("HDFC bank share price",                       "stock_price"),
    ("latest ICICI bank stock price",               "stock_price"),
    ("what does Amazon stock cost",                 "stock_price"),
    ("give me Nvidia stock quote",                  "stock_price"),
    ("look up Apple share value",                   "stock_price"),
    ("fetch Microsoft current price",               "stock_price"),
    ("stock value of Facebook",                     "stock_price"),
    ("what is the market price of TSLA",            "stock_price"),
    ("check AAPL opening price",                    "stock_price"),
    ("today's closing price of Google",             "stock_price"),
    ("day high and day low of Tesla",               "stock_price"),
    ("what is INFY stock trading at",               "stock_price"),
    ("price of crude oil ETF",                      "stock_price"),
    ("what is S&P 500 at right now",                "stock_price"),
    ("how much is gold ETF worth",                  "stock_price"),
    ("price of RELIANCE shares in NSE",             "stock_price"),
    ("check the price for AMD stock",               "stock_price"),
    ("NFLX share price today",                      "stock_price"),
    ("current stock quote for Oracle",              "stock_price"),
    ("what is Salesforce stock price",              "stock_price"),
    ("give me the price of Wipro shares",           "stock_price"),
    ("how much is TATA Motors stock",               "stock_price"),

    # ── market_trend (50 examples) ─────────────────────────────────────────
    ("what is the trend of Apple",                  "market_trend"),
    ("is Tesla bullish or bearish",                 "market_trend"),
    ("market trend for Microsoft stocks",           "market_trend"),
    ("show me the trend analysis of Amazon",        "market_trend"),
    ("is Nvidia going up or down",                  "market_trend"),
    ("what direction is Google stock moving",       "market_trend"),
    ("trend analysis for AAPL",                     "market_trend"),
    ("bullish or bearish for TSLA",                 "market_trend"),
    ("moving average of Apple",                     "market_trend"),
    ("technical analysis of Reliance",              "market_trend"),
    ("is the market bullish for Tesla",             "market_trend"),
    ("market direction for INFY",                   "market_trend"),
    ("what does the SMA say for Apple",             "market_trend"),
    ("EMA trend for Microsoft",                     "market_trend"),
    ("is Amazon on an uptrend",                     "market_trend"),
    ("stock momentum for Google",                   "market_trend"),
    ("is Tesla in a downtrend",                     "market_trend"),
    ("technical indicator for NVDA",                "market_trend"),
    ("show price trend of MSFT over 3 months",      "market_trend"),
    ("is AAPL above its moving average",            "market_trend"),
    ("market analysis for Bitcoin",                 "market_trend"),
    ("is Ethereum in a bullish trend",              "market_trend"),
    ("chart pattern for Tesla",                     "market_trend"),
    ("what is the market outlook for Apple",        "market_trend"),
    ("stock trajectory of Amazon",                  "market_trend"),
    ("is Google stock trending up",                 "market_trend"),
    ("14 day moving average for TSLA",              "market_trend"),
    ("market signal for NVDA",                      "market_trend"),
    ("is RELIANCE in a bullish phase",              "market_trend"),
    ("uptrend or downtrend for TCS",                "market_trend"),
    ("what is the short term trend for AAPL",       "market_trend"),
    ("current market trend of Facebook shares",     "market_trend"),
    ("how is Intel stock trending",                 "market_trend"),
    ("technical outlook for AMD",                   "market_trend"),
    ("is Bitcoin trending bullish",                 "market_trend"),
    ("what does the moving average say for MSFT",   "market_trend"),
    ("is Oracle in a bearish phase",                "market_trend"),
    ("check trend for WIPRO",                       "market_trend"),
    ("what is the medium term trend of HDFC",       "market_trend"),
    ("NFLX price momentum",                         "market_trend"),
    ("is Salesforce above its 50 day moving average", "market_trend"),
    ("trend direction for AMZN",                    "market_trend"),
    ("show me 14 day SMA for Tesla",                "market_trend"),
    ("is Apple trading above EMA",                  "market_trend"),
    ("bearish divergence for Google",               "market_trend"),
    ("market breadth for Nvidia stock",             "market_trend"),
    ("price vs moving average for ICICI",           "market_trend"),
    ("how is TSLA momentum holding up",             "market_trend"),
    ("current trend for INFY shares",               "market_trend"),
    ("is Meta in a bullish rally",                  "market_trend"),

    # ── news_sentiment (50 examples) ───────────────────────────────────────
    ("latest news sentiment about Nvidia",          "news_sentiment"),
    ("what is the sentiment for Tesla news",        "news_sentiment"),
    ("how is the media sentiment for Apple",        "news_sentiment"),
    ("news about Amazon stock sentiment",           "news_sentiment"),
    ("what are people saying about Google",         "news_sentiment"),
    ("market sentiment for Microsoft",              "news_sentiment"),
    ("latest updates on Tesla",                     "news_sentiment"),
    ("analyze this news: Tesla beats earnings",     "news_sentiment"),
    ("sentiment analysis for Nvidia news",          "news_sentiment"),
    ("public sentiment around Apple stock",         "news_sentiment"),
    ("how is TSLA covered by news media",           "news_sentiment"),
    ("what is investor sentiment for Amazon",       "news_sentiment"),
    ("recent headlines for Microsoft",              "news_sentiment"),
    ("is there positive news about Google today",   "news_sentiment"),
    ("news buzz about Nvidia",                      "news_sentiment"),
    ("social media sentiment for Bitcoin",          "news_sentiment"),
    ("what Wall Street thinks about AAPL",          "news_sentiment"),
    ("analyst opinion on TSLA",                     "news_sentiment"),
    ("is there any negative news for Amazon",       "news_sentiment"),
    ("press coverage sentiment for Meta",           "news_sentiment"),
    ("news flow for Intel stock",                   "news_sentiment"),
    ("how are analysts rating AMD",                 "news_sentiment"),
    ("recent CNBC coverage of Tesla",               "news_sentiment"),
    ("Bloomberg sentiment for Apple",               "news_sentiment"),
    ("financial news for NVDA today",               "news_sentiment"),
    ("what is the news saying about MSFT",          "news_sentiment"),
    ("headlines about Ethereum today",              "news_sentiment"),
    ("latest coverage of Reliance industries",      "news_sentiment"),
    ("what news is driving Tesla stock",            "news_sentiment"),
    ("is there good news for Apple investors",      "news_sentiment"),
    ("news sentiment score for Google",             "news_sentiment"),
    ("how does news affect Amazon stock today",     "news_sentiment"),
    ("media coverage of Nvidia earnings",           "news_sentiment"),
    ("what are the latest stories about TSLA",      "news_sentiment"),
    ("financial press sentiment for AMZN",          "news_sentiment"),
    ("current news cycle for Bitcoin",              "news_sentiment"),
    ("how does the press view AAPL this week",      "news_sentiment"),
    ("news based sentiment for TCS",                "news_sentiment"),
    ("Infosys news sentiment today",                "news_sentiment"),
    ("headlines about HDFC bank",                   "news_sentiment"),
    ("recent news for ICICI bank",                  "news_sentiment"),
    ("what news is moving Google stock",            "news_sentiment"),
    ("earnings report sentiment for Microsoft",     "news_sentiment"),
    ("investor reaction to Apple quarterly results", "news_sentiment"),
    ("news driven analysis of Nvidia",              "news_sentiment"),
    ("press response to Tesla recall",              "news_sentiment"),
    ("sentiment from recent AMZN articles",         "news_sentiment"),
    ("how is the media covering Bitcoin",           "news_sentiment"),
    ("NFLX analyst coverage sentiment",             "news_sentiment"),
    ("news about Meta AI announcements",            "news_sentiment"),

    # ── recommendation (50 examples) ───────────────────────────────────────
    ("should I buy Tesla stock",                    "recommendation"),
    ("is it a good time to invest in Apple",        "recommendation"),
    ("should I sell my Amazon shares",              "recommendation"),
    ("is Microsoft a good buy right now",           "recommendation"),
    ("should I invest in Nvidia",                   "recommendation"),
    ("buy or sell AAPL",                            "recommendation"),
    ("is TSLA a good investment",                   "recommendation"),
    ("would you recommend buying Google",           "recommendation"),
    ("is Reliance stock worth buying",              "recommendation"),
    ("should I invest in TATA Motors",              "recommendation"),
    ("is this a good time to buy Infosys",          "recommendation"),
    ("what do you think about buying AMZN",         "recommendation"),
    ("is Apple undervalued right now",              "recommendation"),
    ("should I hold or sell my Tesla shares",       "recommendation"),
    ("is Google a good long term investment",       "recommendation"),
    ("is Amazon a buy at current price",            "recommendation"),
    ("should I add more Microsoft to my portfolio", "recommendation"),
    ("is Nvidia overvalued",                        "recommendation"),
    ("would you buy AMD at this price",             "recommendation"),
    ("give me a buy or sell recommendation for Meta","recommendation"),
    ("is Bitcoin a safe investment",                "recommendation"),
    ("should I put money in Ethereum",              "recommendation"),
    ("is now a good time to invest in Tesla",       "recommendation"),
    ("is Infosys worth buying for long term",       "recommendation"),
    ("should I buy more TCS shares",                "recommendation"),
    ("is WIPRO a buy or sell today",                "recommendation"),
    ("would you recommend HDFC bank stock",         "recommendation"),
    ("is ICICI bank a good buy",                    "recommendation"),
    ("should I exit my Amazon position",            "recommendation"),
    ("is it safe to buy Google now",                "recommendation"),
    ("investment advice for Nvidia stock",          "recommendation"),
    ("should retail investors buy Apple now",       "recommendation"),
    ("is MSFT a good stock for beginners",          "recommendation"),
    ("would you invest in Netflix at this price",   "recommendation"),
    ("is Salesforce worth the premium",             "recommendation"),
    ("should I take profits on TSLA",               "recommendation"),
    ("is Intel a value buy",                        "recommendation"),
    ("buy recommendation for NVDA",                 "recommendation"),
    ("should I invest 1000 dollars in Apple",       "recommendation"),
    ("is Google stock a bargain right now",         "recommendation"),
    ("which is better to buy Apple or Microsoft",   "recommendation"),
    ("should I diversify into Amazon",              "recommendation"),
    ("is Tesla a buy after recent dip",             "recommendation"),
    ("what is your stock pick for today",           "recommendation"),
    ("investment opinion on Reliance",              "recommendation"),
    ("is AMZN worth buying before earnings",        "recommendation"),
    ("should I sell NVDA after rally",              "recommendation"),
    ("buy hold or sell AAPL today",                 "recommendation"),
    ("TATA stock buy recommendation",               "recommendation"),
    ("is it too late to buy Bitcoin",               "recommendation"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  TICKER MAP — company name aliases → official ticker symbol
# ══════════════════════════════════════════════════════════════════════════════

TICKER_MAP: dict[str, str] = {
    # US Tech
    "apple": "AAPL",  "aapl": "AAPL",
    "tesla": "TSLA",  "tsla": "TSLA",
    "microsoft": "MSFT", "msft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "googl": "GOOGL",
    "amazon": "AMZN",  "amzn": "AMZN",
    "nvidia": "NVDA",  "nvda": "NVDA",
    "meta": "META",    "facebook": "META",
    "netflix": "NFLX", "nflx": "NFLX",
    "intel": "INTC",   "intc": "INTC",
    "amd": "AMD",
    "salesforce": "CRM",
    "oracle": "ORCL",
    # Indian stocks (NSE via yfinance suffix .NS)
    "tata": "TMPV.NS",
    "tata motors": "TMPV.NS",
    "reliance": "RELIANCE.NS",
    "infosys": "INFY.NS",       "infy": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hdfc": "HDFCBANK.NS",
    "tcs": "TCS.NS",
    "icici": "ICICIBANK.NS",
    # Crypto (via yfinance)
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
}


# ══════════════════════════════════════════════════════════════════════════════
#  INTENT CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

class IntentClassifier:
    """TF-IDF vectoriser + Multinomial Naive Bayes intent classifier. Persists to disk."""

    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), lowercase=True, min_df=1)),
            ("clf",   MultinomialNB(alpha=0.05)),
        ])
        self.label_encoder = LabelEncoder()
        self._trained = False

    def train(self, data: list[tuple[str, str]], force: bool = False) -> None:
        """Train (or load from disk if already trained)."""
        if not force and os.path.exists(CLASSIFIER_PATH):
            bundle = joblib.load(CLASSIFIER_PATH)
            self.pipeline      = bundle["pipeline"]
            self.label_encoder = bundle["label_encoder"]
            self._trained = True
            print(f"  ✅ Classifier loaded from {CLASSIFIER_PATH}")
            return

        texts, labels = zip(*data)
        encoded = self.label_encoder.fit_transform(labels)
        self.pipeline.fit(texts, encoded)
        self._trained = True

        # Save to disk
        joblib.dump({"pipeline": self.pipeline, "label_encoder": self.label_encoder}, CLASSIFIER_PATH)
        print(f"  💾 Classifier saved → {CLASSIFIER_PATH}  ({len(data)} examples)")

    def predict(self, text: str) -> tuple[str, float]:
        """Return (intent_label, confidence_score)."""
        if not self._trained:
            raise RuntimeError("Classifier has not been trained yet.")
        encoded = self.pipeline.predict([text])[0]
        proba   = self.pipeline.predict_proba([text])[0].max()
        label   = self.label_encoder.inverse_transform([encoded])[0]
        return label, round(float(proba), 4)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTITY EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════

def extract_ticker(text: str) -> str | None:
    """
    Extract a stock ticker/company from user input.

    Priority order:
        1. Direct ticker match (e.g. "AAPL", "NVDA")
        2. Ticker map lookup (company name → ticker)
        3. spaCy NER ORG entity → ticker map lookup
    """
    lower = text.lower()

    # 1 — Check for explicit ticker symbols (3-5 uppercase letters)
    explicit = re.findall(r'\b([A-Z]{2,5}(?:\.[A-Z]{1,2})?)\b', text)
    for match in explicit:
        if match.upper() in {v.upper() for v in TICKER_MAP.values()}:
            return match.upper()

    # 2 — Company name keyword match in ticker map (longest match first)
    sorted_names = sorted(TICKER_MAP.keys(), key=len, reverse=True)
    for name in sorted_names:
        if name in lower:
            return TICKER_MAP[name]

    # 3 — spaCy NER fallback
    nlp_result = nlp_analyze(text)
    for company in nlp_result.get("companies", []):
        ticker = TICKER_MAP.get(company.lower())
        if ticker:
            return ticker
        # Use the raw ORG name as a ticker guess (e.g. "RELIANCE")
        return company.upper()

    return None


# ══════════════════════════════════════════════════════════════════════════════
#  RESPONSE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _respond_stock_price(ticker: str) -> dict:
    data = get_stock_price(ticker)
    if "error" in data:
        return {
            "intent": "stock_price",
            "ticker": ticker,
            "response": f"Sorry, I couldn't fetch the stock price for '{ticker}'. "
                        f"Please check the ticker symbol and try again.",
            "data": data,
        }
    chg_icon = "📈" if data["change"] >= 0 else "📉"
    sign     = "+" if data["change"] >= 0 else ""
    reply = (
        f"{chg_icon} **{data['name']} ({data['symbol']})**\n"
        f"   Current Price : {data['currency']} {data['price']}\n"
        f"   Open / High / Low : {data['open']} / {data['high']} / {data['low']}\n"
        f"   Volume  : {data['volume']:,}\n"
        f"   Change  : {sign}{data['change']} ({sign}{data['change_pct']}%)"
    )
    return {"intent": "stock_price", "ticker": ticker, "response": reply, "data": data}


def _respond_market_trend(ticker: str) -> dict:
    report = full_analysis(ticker, period="3mo", window=14)
    if "error" in report:
        return {
            "intent": "market_trend",
            "ticker": ticker,
            "response": f"Sorry, I couldn't fetch trend data for '{ticker}'.",
            "data": report,
        }
    sma = report["sma_trend"]
    ema = report["ema_trend"]
    icons = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}

    reply = (
        f"📊 **Market Trend — {ticker}** (last 3 months, 14-day window)\n"
        f"   Latest Price : ${report['latest_price']}\n"
        f"   SMA-14 Trend : {icons[sma['trend']]} {sma['trend'].upper()}  "
        f"(price vs MA: {sma['deviation_pct']:+.2f}%)\n"
        f"   EMA-14 Trend : {icons[ema['trend']]} {ema['trend'].upper()}  "
        f"(price vs EMA: {ema['deviation_pct']:+.2f}%)\n"
        f"   Recent Prices: {report['recent_prices']}\n\n"
        f"   ℹ️  This describes where price sits relative to its recent average. "
        f"In back-tests on 19 stocks (10 yrs) such signals did not predict "
        f"future direction better than chance."
    )
    return {"intent": "market_trend", "ticker": ticker, "response": reply, "data": report}


def _respond_news_sentiment(ticker: str, user_text: str) -> dict:
    # Fetch real news + run sentiment on headlines
    company_map = {v: k.title() for k, v in TICKER_MAP.items() if len(k) > 3}
    company_name = company_map.get(ticker, ticker)
    news_data = fetch_news(ticker, company_name, limit=5)

    icons = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}
    overall = news_data.get("overall_sentiment", {})
    icon    = icons.get(overall.get("sentiment", "neutral"), "🟡")

    articles = news_data.get("articles", [])
    article_lines = ""
    for i, a in enumerate(articles[:4], 1):
        sent  = a.get("sentiment", {})
        s_ico = icons.get(sent.get("sentiment", "neutral"), "🟡")
        article_lines += f"\n   {i}. {a['title'][:70]}\n      {s_ico} {sent.get('sentiment','').upper()} ({sent.get('score',0):+.2f})  — {a.get('source','')}"

    reply = (
        f"📰 **News Sentiment — {ticker}**\n"
        f"   Overall Sentiment : {icon} {overall.get('sentiment','').upper()} "
        f"(score: {overall.get('score',0):+.4f})\n"
        f"   Articles analysed : {news_data.get('total', 0)}\n"
        f"   Latest Headlines  :{article_lines}\n"
    )
    return {
        "intent"  : "news_sentiment",
        "ticker"  : ticker,
        "response": reply,
        "data"    : news_data,
    }


def _respond_recommendation(ticker: str) -> dict:
    """
    Combine price, trend, and sentiment for a simple buy/hold/sell signal.
    NOT financial advice — for educational purposes only.
    """
    price_data  = get_stock_price(ticker)
    trend_data  = full_analysis(ticker, period="3mo", window=14)
    sentiment   = analyze_sentiment(f"{ticker} stock performance and outlook")

    signals = []

    # Trend signal
    sma_trend = trend_data.get("sma_trend", {}).get("trend", "neutral")
    ema_trend = trend_data.get("ema_trend", {}).get("trend", "neutral")
    if sma_trend == "bullish" and ema_trend == "bullish":
        signals.append(("trend",     "BUY",  "Both SMA & EMA are bullish"))
    elif sma_trend == "bearish" and ema_trend == "bearish":
        signals.append(("trend",     "SELL", "Both SMA & EMA are bearish"))
    else:
        signals.append(("trend",     "HOLD", "Mixed or neutral MA signals"))

    # Sentiment signal
    sent = sentiment["sentiment"]
    if sent == "positive":
        signals.append(("sentiment", "BUY",  "Positive market sentiment"))
    elif sent == "negative":
        signals.append(("sentiment", "SELL", "Negative market sentiment"))
    else:
        signals.append(("sentiment", "HOLD", "Neutral sentiment"))

    # Price change signal
    change_pct = price_data.get("change_pct", 0) if "error" not in price_data else 0
    if change_pct > 1.0:
        signals.append(("momentum",  "BUY",  f"Price up {change_pct:+.2f}% today"))
    elif change_pct < -1.0:
        signals.append(("momentum",  "SELL", f"Price down {change_pct:+.2f}% today"))
    else:
        signals.append(("momentum",  "HOLD", f"Price change minimal ({change_pct:+.2f}%)"))

    # Aggregate
    buys  = sum(1 for _, action, _ in signals if action == "BUY")
    sells = sum(1 for _, action, _ in signals if action == "SELL")
    final = "BUY 🟢" if buys > sells else "SELL 🔴" if sells > buys else "HOLD 🟡"

    # Price prediction signal
    pred = predict_next_price(ticker)
    pred_note = ""
    if "error" not in pred:
        arrow  = "⬆" if pred["direction"] == "up" else "⬇" if pred["direction"] == "down" else "➡"
        pred_note = (
            f"\n   🧠 ML Price Forecast (next day):\n"
            f"      {arrow} Current: ${pred['current_price']}  →  Predicted: ${pred['predicted_price']} "
            f"({pred['predicted_change_pct']:+.2f}%)\n"
            f"      Model: {pred['model_used']}  |  R²={pred['r2_score']}  |  Confidence: {pred['confidence']}\n"
        )
        if pred["direction"] == "up":
            signals.append(("ml_forecast", "BUY",  f"ML predicts price up {pred['predicted_change_pct']:+.2f}%"))
        elif pred["direction"] == "down":
            signals.append(("ml_forecast", "SELL", f"ML predicts price down {pred['predicted_change_pct']:+.2f}%"))
        else:
            signals.append(("ml_forecast", "HOLD", "ML predicts flat price movement"))
        buys  = sum(1 for _, action, _ in signals if action == "BUY")
        sells = sum(1 for _, action, _ in signals if action == "SELL")
        final = "BUY 🟢" if buys > sells else "SELL 🔴" if sells > buys else "HOLD 🟡"

    price_str = f"{price_data['currency']} {price_data['price']}" if "error" not in price_data else "N/A"

    signals_text = "\n".join(
        f"   [{s[1]:>4}]  {s[0].capitalize():10} — {s[2]}" for s in signals
    )

    reply = (
        f"💡 **Recommendation — {ticker}**\n"
        f"   Current Price : {price_str}\n\n"
        f"   Signal Breakdown:\n{signals_text}\n\n"
        f"   ─────────────────────────────\n"
        f"   📌 Final Signal : {final}\n\n"
        f"   ⚠️  Trend/momentum signals are descriptive, not predictive (see README). "
        f"This is for educational purposes only. "
        f"Always do your own research before investing."
    )

    return {
        "intent": "recommendation",
        "ticker": ticker,
        "final_signal": final.split()[0],
        "response": reply,
        "signals": [{"factor": s[0], "action": s[1], "reason": s[2]} for s in signals],
    }


def _respond_unknown(text: str) -> dict:
    return {
        "intent": "unknown",
        "response": (
            "🤖 I'm your Financial Assistant! I can help you with:\n"
            "   • Stock prices  — 'What is Tesla stock price?'\n"
            "   • Market trends — 'Is Apple bullish or bearish?'\n"
            "   • Sentiment     — 'Latest news sentiment about Nvidia'\n"
            "   • Advice        — 'Should I buy Amazon stock?'\n\n"
            "   Please try rephrasing your question!"
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CHATBOT CLASS
# ══════════════════════════════════════════════════════════════════════════════

class FinancialChatbot:
    """
    End-to-end financial chatbot.

    Usage:
        bot = FinancialChatbot()
        result = bot.chat("What is Tesla stock price?")
        print(result["response"])
    """

    LOW_CONFIDENCE_THRESHOLD = 0.35

    def __init__(self):
        self.classifier = IntentClassifier()
        self.classifier.train(TRAINING_DATA)   # loads from disk if available
        self.history: list[dict] = []

    def chat(self, user_input: str) -> dict:
        """
        Process a user message and return a structured chatbot response.

        Args:
            user_input (str): Raw user query.

        Returns:
            dict: {
                "input"     : str,
                "intent"    : str,
                "confidence": float,
                "ticker"    : str | None,
                "response"  : str,
                ...extra keys depending on intent
            }
        """
        text = user_input.strip()
        if not text:
            return {"input": text, "response": "Please enter a question."}

        # ── 1. Intent detection
        intent, confidence = self.classifier.predict(text)
        if confidence < self.LOW_CONFIDENCE_THRESHOLD:
            intent = "unknown"

        # ── 2. Entity extraction
        ticker = extract_ticker(text)

        # ── 3. Route to correct handler
        if intent == "stock_price" and ticker:
            result = _respond_stock_price(ticker)
        elif intent == "market_trend" and ticker:
            result = _respond_market_trend(ticker)
        elif intent == "news_sentiment" and ticker:
            result = _respond_news_sentiment(ticker, text)
        elif intent == "recommendation" and ticker:
            result = _respond_recommendation(ticker)
        elif ticker and intent != "unknown":
            # Intent detected but no ticker — ask for clarification
            result = {
                "intent": intent,
                "response": f"I understood you're asking about **{intent.replace('_', ' ')}**, "
                            f"but I couldn't identify a stock symbol. "
                            f"Could you mention the company name or ticker?",
            }
        else:
            result = _respond_unknown(text)

        # ── 4. Attach metadata and save to history
        result.update({
            "input"     : text,
            "intent"    : intent,
            "confidence": confidence,
            "ticker"    : ticker,
        })
        self.history.append(result)
        return result


# ══════════════════════════════════════════════════════════════════════════════
#  DEMO
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    bot = FinancialChatbot()

    queries = [
        "What is Tesla stock price?",
        "Is Apple bullish or bearish right now?",
        "Latest news about Nvidia",
        "Should I buy Amazon stock?",
        "Stock price of TATA",
        "trend of Microsoft",
        "Should I invest in Bitcoin?",
        "Hello, what can you do?",
    ]

    print("\n" + "═" * 65)
    print("  🤖  Financial Chatbot — Live Demo")
    print("═" * 65)

    for query in queries:
        print(f"\n{'─' * 65}")
        print(f"  👤 User   : {query}")
        result = bot.chat(query)
        print(f"  🎯 Intent : {result['intent']}  (confidence: {result['confidence']:.0%})")
        print(f"  🏷  Ticker : {result['ticker']}")
        print(f"  🤖 Bot    :\n")
        for line in result["response"].split("\n"):
            print(f"     {line}")
