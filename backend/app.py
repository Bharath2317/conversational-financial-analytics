"""
app.py — Financial Chatbot FastAPI Server

Endpoints:
  GET  /            → Serve chatbot frontend HTML
  POST /chat        → Main chatbot endpoint
  GET  /alerts      → Retrieve all triggered alerts
  GET  /metrics     → Return evaluation metrics
  GET  /health      → Health check
  GET  /stock/{sym} → Direct stock price lookup
"""

import os
import sys

# Allow imports from the backend/ directory regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot       import FinancialChatbot
from stock_api     import get_stock_price, get_stock_history
from alert_system  import run_all_checks, get_all_alerts, clear_alerts
from sentiment_analysis import analyze_sentiment
from market_analyzer    import full_analysis
from news_fetcher       import fetch_news
from price_predictor    import predict_next_price, train_model

# ─── App init ────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "FinBot — Financial Chatbot API",
    description = "AI-powered financial assistant with NLP, sentiment analysis & trend detection.",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Initialise the chatbot (trains classifier once at startup)
bot = FinancialChatbot()

# ─── Request / Response models ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent:   str
    ticker:   str | None
    confidence: float
    alerts:   list[dict] = []
    data:     dict       = {}

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def serve_frontend():
    """Serve the chatbot HTML frontend."""
    html_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return JSONResponse({"message": "FinBot API is running. Frontend not found."})


@app.post("/chat", response_model=ChatResponse, tags=["Chatbot"])
async def chat(req: ChatRequest):
    """
    Main chatbot endpoint.

    Runs the full pipeline:
      1. NLP + intent detection
      2. Entity (ticker) extraction
      3. Live stock / trend / sentiment data fetch
      4. Alert checks
      5. Natural language response generation
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # ── Run chatbot pipeline
    result = bot.chat(req.message)

    ticker    = result.get("ticker")
    triggered = []

    # ── Run alert system if we have a ticker + data
    if ticker:
        price_data    = get_stock_price(ticker)
        sentiment_data = analyze_sentiment(req.message)
        trend_report  = full_analysis(ticker, period="3mo", window=14)
        triggered     = run_all_checks(ticker, price_data, sentiment_data, trend_report)

    return ChatResponse(
        response   = result.get("response", ""),
        intent     = result.get("intent", "unknown"),
        ticker     = ticker,
        confidence = result.get("confidence", 0.0),
        alerts     = triggered,
        data       = {k: v for k, v in result.items()
                      if k not in ("response", "intent", "ticker", "confidence", "input")},
    )


@app.get("/alerts", tags=["Alerts"])
async def get_alerts(ticker: str | None = None):
    """Retrieve all triggered alerts. Filter by ticker with ?ticker=TSLA"""
    alerts = get_all_alerts()
    if ticker:
        alerts = [a for a in alerts if a["ticker"].upper() == ticker.upper()]
    return {"total": len(alerts), "alerts": alerts}


@app.delete("/alerts", tags=["Alerts"])
async def clear_all_alerts():
    """Clear the in-memory alert store."""
    clear_alerts()
    return {"message": "All alerts cleared."}


@app.get("/metrics", tags=["Analytics"])
async def get_metrics():
    """Return system evaluation metrics for reporting / paper.

    Serves measured results from data/evaluation.json (produced by
    `python backend/evaluate.py`) when present; otherwise falls back to the
    figures quoted in the dissertation, clearly labelled as such.
    """
    import json
    eval_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "evaluation.json")
    if os.path.exists(eval_path):
        with open(eval_path, encoding="utf-8") as fh:
            return {"source": "measured (backend/evaluate.py)", **json.load(fh)}
    return {
        "source": "reported in dissertation (not yet measured — run backend/evaluate.py)",
        "model": "FinBot v1.0 — Financial Chatbot",
        "evaluation_metrics": {
            "intent_detection_accuracy":   {"value": 92, "unit": "%"},
            "entity_recognition_f1":       {"value": 90, "unit": "%"},
            "trend_prediction_accuracy":   {"value": 82, "unit": "%"},
            "response_relevance":          {"value": 81, "unit": "%"},
            "chatbot_success_rate":        {"value": 87, "unit": "%"},
        },
        "classifier": {
            "model":         "TF-IDF + Multinomial Naive Bayes",
            "intents":       ["stock_price", "market_trend", "news_sentiment", "recommendation"],
            "vectorizer":    "TfidfVectorizer (1-3 ngrams)",
        },
        "nlp": {
            "tokenizer":    "NLTK punkt",
            "lemmatizer":   "NLTK WordNet",
            "ner_model":    "spaCy en_core_web_sm",
            "stopwords":    "NLTK English",
        },
        "data_sources": ["yfinance (live market data)"],
        "sentiment_engines": ["NLTK VADER (65% weight)", "TextBlob (35% weight)"],
    }


@app.get("/stock/{symbol}", tags=["Market Data"])
async def stock_price(symbol: str):
    """Direct stock price lookup endpoint."""
    data = get_stock_price(symbol.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/news/{symbol}", tags=["Market Data"])
async def stock_news(symbol: str, limit: int = 5):
    """Fetch real news headlines + sentiment for a stock symbol."""
    from stock_api import get_stock_price
    info = get_stock_price(symbol.upper())
    company = info.get("name", symbol) if "error" not in info else symbol
    data = fetch_news(symbol.upper(), company, limit=limit)
    return data


@app.get("/predict/{symbol}", tags=["Market Data"])
async def price_prediction(symbol: str):
    """ML-based next-day price prediction for a stock symbol."""
    data = predict_next_price(symbol.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.post("/train/{symbol}", tags=["Market Data"])
async def train_stock_model(symbol: str, period: str = "2y"):
    """Train (or retrain) the price prediction model for a ticker."""
    result = train_model(symbol.upper(), period=period)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/stock/{symbol}/history", tags=["Market Data"])
async def stock_history(symbol: str, period: str = "7d"):
    """Fetch OHLCV history for a stock symbol."""
    from stock_api import get_stock_history
    data = get_stock_history(symbol.upper(), period)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/stock/{symbol}/trend", tags=["Market Data"])
async def stock_trend(symbol: str, period: str = "3mo"):
    """Full trend analysis for a stock symbol."""
    data = full_analysis(symbol.upper(), period=period)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.api_route("/health", methods=["GET", "HEAD"], tags=["System"])
async def health():
    return {"status": "ok", "service": "FinBot Financial Chatbot API"}


# ─── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
