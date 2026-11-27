# 🤖 FinBot — AI-Powered Financial Chatbot

> An intelligent financial assistant that understands natural language, fetches live stock data, analyzes market trends, detects sentiment from real news, and gives ML-powered investment recommendations.

## 🎓 Project Details

|                |                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------- |
| **Title**      | Conversational Financial Analytics and Market Trend Interpretation Using NLP Pipelines (FinBot)   |
| **Degree**     | B.Tech in CSE – Data Science (2025–2026), JNTU Kakinada                                           |
| **Institute**  | KKR & KSR Institute of Technology and Sciences (Autonomous), Vinjanampadu, Guntur, A.P.           |
| **Guide**      | Mrs. P. Anuradha, Assistant Professor, Dept. of CSE – Data Science                                |
| **Team**       | Settipalli Hemanth (22JR1A44C0), Rayi Tejesh (22JR1A44B7), Madanu Divya Kiran Kumar (23JR5A4409), Paritala Bharath (22JR1A44A9) |
| **Submitted**  | April 2026                                                                                        |

**Abstract (from the dissertation):** The system lets users query financial market data in natural language instead of navigating several platforms or dashboards. Using NLP pipelines (intent recognition, entity extraction, response generation) and REST APIs, the chatbot returns real-time stock information, market trends, news sentiment and predictions.

**Keywords:** Conversational AI, Natural Language Processing, Market Intelligence, Financial Text Analytics, Predictive Modeling.

> **Note:** The dissertation names the OpenDialog framework for dialogue management. This codebase implements the dialogue layer itself (FastAPI + a TF-IDF/Naive Bayes intent classifier in `backend/chatbot.py`) and does not use OpenDialog.

**Results reported in the dissertation (Chapter 5):**

| Module                  | Reported result                                    |
| ----------------------- | -------------------------------------------------- |
| Intent classification   | Acc 92%, Precision 91%, Recall 93%, F1 92%         |
| Entity extraction       | Acc 90%, Precision 89%, Recall 91%, F1 90%         |
| Market trend analysis   | ~82% accuracy                                      |
| Response relevance      | ~81%                                               |
| Conversation success    | ~87%                                               |

> These figures are quoted from the report. `backend/evaluate.py` measures them independently — see [Evaluation Metrics](#evaluation-metrics); the intent result is close, the trend result is not reproduced.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Example Conversations](#example-conversations)
- [ML Models](#ml-models)
- [Evaluation Metrics](#evaluation-metrics)
- [No API Keys Required](#no-api-keys-required)

---

## 🧠 Overview

**FinBot** is a full-stack AI financial chatbot built with Python. It bridges natural language understanding with real-time financial data to help users make sense of the stock market through conversation.

A user can type a question like:

> _"Should I buy Tesla stock?"_

And FinBot will:

1. Detect the **intent** (`recommendation`)
2. Extract the **entity** (`TSLA`)
3. Fetch the **live price** from Yahoo Finance
4. Analyze the **SMA/EMA market trend**
5. Pull **real news headlines** and score their sentiment
6. Run an **ML price prediction** model (Random Forest / Ridge)
7. Combine all signals and return a **BUY / HOLD / SELL** recommendation

---

## 📁 Project Structure

```
c:\Projects\KITS\Fintech\
│
├── backend/                        ← All Python backend modules
│   ├── app.py                      ← FastAPI server (9 REST endpoints)
│   ├── chatbot.py                  ← Main chatbot — intent detection + routing
│   ├── stock_api.py                ← Live stock price & OHLCV data (yfinance)
│   ├── market_analyzer.py          ← SMA, EMA, trend detection
│   ├── sentiment_analysis.py       ← VADER + TextBlob dual-engine sentiment
│   ├── nlp_pipeline.py             ← Tokenize, lemmatize, NER, keyword detection
│   ├── news_fetcher.py             ← Real RSS news headlines + sentiment scoring
│   ├── price_predictor.py          ← ML model: train, save, predict next price
│   ├── alert_system.py             ← Spike/sentiment alerts with disk persistence
│   └── demo_nlp.py                 ← Standalone NLP demo script
│
├── data/                           ← Auto-generated live data (committed after first run)
│   ├── AAPL_history.csv            ← 2 years Apple OHLCV history (501 rows)
│   ├── TSLA_history.csv            ← 2 years Tesla OHLCV history
│   ├── MSFT_history.csv            ← 2 years Microsoft OHLCV history
│   └── alerts.json                 ← Persistent alert log
│
├── models/                         ← Trained ML model files (auto-saved)
│   ├── intent_classifier.pkl       ← TF-IDF + Naive Bayes (201 training examples)
│   ├── AAPL_predictor.pkl          ← Price prediction model for Apple (R²=0.89)
│   ├── TSLA_predictor.pkl          ← Price prediction model for Tesla
│   ├── MSFT_predictor.pkl          ← Price prediction model for Microsoft (R²=0.96)
│   ├── AAPL_meta.json              ← Model metadata & performance report
│   ├── TSLA_meta.json
│   └── MSFT_meta.json
│
├── frontend/
│   └── index.html                  ← ChatGPT-style dark UI (HTML + JavaScript)
│
├── requirements.txt                ← All Python dependencies
└── README.md                       ← This file
```

---

## 🛠 Tech Stack

| Layer              | Technology                            | Purpose                        |
| ------------------ | ------------------------------------- | ------------------------------ |
| **Backend**        | FastAPI + Uvicorn                     | REST API server                |
| **NLP — Intent**   | scikit-learn TF-IDF + Naive Bayes     | Classify user intent           |
| **NLP — Pipeline** | spaCy `en_core_web_sm`, NLTK          | Tokenize, lemmatize, NER       |
| **Sentiment**      | NLTK VADER + TextBlob                 | Dual-engine sentiment scoring  |
| **Market Data**    | yfinance                              | Live prices, OHLCV history     |
| **News**           | feedparser (Yahoo + Google RSS)       | Real headlines — no API key    |
| **ML Prediction**  | scikit-learn RandomForest, GBM, Ridge | Next-day price forecast        |
| **Model Storage**  | joblib                                | Save/load `.pkl` model files   |
| **Alerts**         | Custom Python module                  | Price spike + sentiment alerts |
| **Frontend**       | HTML5 + Vanilla JS                    | Chat interface                 |

---

## ✨ Features

### 💬 Conversational Chat

- Natural language understanding — no need to use exact commands
- 4 intent classes: `stock_price`, `market_trend`, `news_sentiment`, `recommendation`
- **Any global stock**: ~120 common names resolve instantly; any other ticker (e.g. `SBUX`, `7203.T`, `SOL-USD`) or company name (e.g. "Zalando", "Logitech", "Airbus") is verified/resolved through Yahoo Finance search
- Graceful fallback for unknown queries

### 📈 Live Stock Data

- Real-time price, open, high, low, volume, change %
- Full OHLCV history (configurable period: `1d` to `5y`)
- Supports: AAPL, TSLA, MSFT, GOOGL, AMZN, NVDA, META, NFLX, RELIANCE.NS, TMPV.NS, INFY.NS, BTC-USD, ETH-USD, and more

### 📊 Market Trend Analysis

- **Simple Moving Average (SMA)** and **Exponential Moving Average (EMA)**
- 14-day window trend detection → `bullish` / `bearish` / `neutral`
- Dead-band threshold (0.5%) to avoid noisy signals
- Price deviation percentage from moving average

### 📰 Real News Sentiment

- Fetches live headlines from **Yahoo Finance RSS** and **Google News RSS**
- No API key required
- Per-article sentiment scored individually with label + numeric score
- Overall sentiment aggregated across all articles

### 🧠 ML Price Prediction

- Features: 15+ engineered indicators (lag prices, rolling SMA/EMA, volatility, returns, calendar features)
- Trains **3 models** (Random Forest, Gradient Boosting, Ridge) and picks the best by R² score
- Models **auto-saved** to `models/` on first run — loads instantly after that
- Trains new ticker on-demand via `POST /train/{symbol}`

### 🚨 Alert System

- Fires on: price change >5% (`WARNING`), >10% (`CRITICAL`), negative sentiment
- Alerts persisted to `data/alerts.json` — survive server restarts
- Viewable via `GET /alerts` endpoint and displayed in the chat UI sidebar

### 🖥 Premium Chat UI

- ChatGPT-style dark interface
- Sidebar with quick queries, live model metrics, real-time alert feed
- Intent + ticker + confidence tags on each bot response
- Typing animation, smooth transitions

---

## 🏗 Architecture

```
User Message (HTTP POST /chat)
        │
        ▼
┌──────────────────────┐
│   Intent Classifier  │  TF-IDF (1-3 ngrams) + Naive Bayes
│   (chatbot.py)       │  201 labelled training examples
└────────┬─────────────┘
         │ intent: stock_price / market_trend / news_sentiment / recommendation
         ▼
┌──────────────────────┐
│   Entity Extractor   │  Regex → TICKER_MAP → spaCy NER
│   (chatbot.py)       │  TSLA, AAPL, RELIANCE.NS, BTC-USD …
└────────┬─────────────┘
         │ ticker symbol
         ▼
┌──────────────────────────────────────────────┐
│               Module Dispatcher              │
│                                              │
│  stock_price    → stock_api.py               │
│  market_trend   → market_analyzer.py         │
│  news_sentiment → news_fetcher.py            │
│  recommendation → stock_api + market_analyzer│
│                   + sentiment_analysis       │
│                   + price_predictor          │
└────────┬─────────────────────────────────────┘
         │ structured response dict
         ▼
┌──────────────────────┐
│   Alert Checker      │  alert_system.py
│   (parallel)         │  Price >5% change or negative sentiment
└────────┬─────────────┘
         │
         ▼
    JSON Response → Frontend Chat UI
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Steps

**1. Clone or open the project**

```powershell
cd c:\Projects\KITS\Fintech
```

**2. Install all dependencies**

```powershell
pip install -r requirements.txt
```

**3. Download the spaCy NLP model** (one-time)

```powershell
python -m spacy download en_core_web_sm
```

**That's it.** No API keys, no database setup, no environment variables needed.

---

## ▶️ Running the Application

```powershell
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Then open your browser at:

```
http://localhost:8000
```

> **First run note:** The intent classifier and price prediction models are auto-trained and saved on first startup. Subsequent starts load from disk (instant).

---

## 🔌 API Reference

| Method   | Endpoint                            | Description                                       |
| -------- | ----------------------------------- | ------------------------------------------------- |
| `GET`    | `/`                                 | Serve chat frontend (HTML)                        |
| `POST`   | `/chat`                             | **Main chatbot** — send a message, get a response |
| `GET`    | `/stock/{symbol}`                   | Live price snapshot for any ticker                |
| `GET`    | `/stock/{symbol}/history?period=7d` | OHLCV history                                     |
| `GET`    | `/stock/{symbol}/trend?period=3mo`  | SMA + EMA trend analysis                          |
| `GET`    | `/news/{symbol}?limit=5`            | Real news headlines + sentiment                   |
| `GET`    | `/predict/{symbol}`                 | ML next-day price prediction                      |
| `POST`   | `/train/{symbol}?period=2y`         | Train/retrain ML model for a new ticker           |
| `GET`    | `/alerts?ticker=TSLA`               | List all triggered alerts                         |
| `DELETE` | `/alerts`                           | Clear all alerts                                  |
| `GET`    | `/metrics`                          | System evaluation metrics (for reports)           |
| `GET`    | `/health`                           | Server health check                               |
| `GET`    | `/docs`                             | **Swagger interactive API documentation**         |

### POST `/chat` — Example

**Request:**

```json
{
  "message": "What is Tesla stock price?"
}
```

**Response:**

```json
{
  "response": "📈 Tesla, Inc. (TSLA)\n   Current Price : USD 405.94\n   Open / High / Low : 397.845 / 408.33 / 394.59\n   Volume  : 67,670,354\n   Change  : +13.51 (+3.44%)",
  "intent": "stock_price",
  "ticker": "TSLA",
  "confidence": 0.69,
  "alerts": [],
  "data": { ... }
}
```

---

## 💬 Example Conversations

| User says                        | Intent           | Ticker        | Bot does                            |
| -------------------------------- | ---------------- | ------------- | ----------------------------------- |
| _"What is Tesla stock price?"_   | `stock_price`    | TSLA          | Fetches live OHLCV from yfinance    |
| _"Is Apple bullish or bearish?"_ | `market_trend`   | AAPL          | Computes SMA-14 + EMA-14 trend      |
| _"Latest news about Nvidia"_     | `news_sentiment` | NVDA          | Fetches real RSS headlines + scores |
| _"Should I buy Amazon?"_         | `recommendation` | AMZN          | BUY/HOLD/SELL using 4 signals       |
| _"TATA stock price"_             | `stock_price`    | TMPV.NS | Handles Indian NSE stocks           |
| _"Is Bitcoin safe to invest?"_   | `recommendation` | BTC-USD       | Works with crypto too               |

---

## 🤖 ML Models

### Intent Classifier

- **Algorithm**: TF-IDF Vectorizer (1–3 ngrams) + Multinomial Naive Bayes
- **Training data**: 201 manually labelled sentences (50 per intent)
- **Intents**: `stock_price`, `market_trend`, `news_sentiment`, `recommendation`
- **Saved to**: `models/intent_classifier.pkl`

### Price Prediction Model

- **Features (15+)**:
  - Lag close prices (1, 2, 3, 5, 10 days)
  - Rolling SMA/std (5, 10, 20, 50 day)
  - Daily, 5-day, 10-day returns
  - Volatility (5-day, 20-day)
  - High-Low ratio, Close-Open ratio
  - Volume MA + ratio
  - Calendar: day of week, month, quarter
- **Models trained**: Random Forest, Gradient Boosting, Ridge Regression
- **Best selected** by R² on 20% holdout test set
- **Saved to**: `models/{TICKER}_predictor.pkl`

| Ticker | Best Model | R² Score (saved `*_meta.json`) |
| ------ | ---------- | ------------------------------ |
| AAPL   | Ridge      | 0.792                          |
| TSLA   | Ridge      | 0.788                          |
| MSFT   | Ridge      | 0.955                          |

> Random Forest and Gradient Boosting scored negative R² on AAPL's hold-out period, because tree models cannot extrapolate beyond the training price range. R² on absolute price is also inflated by the lag/moving-average features; it is not evidence of forecasting skill.

------ | ------------------- | -------- |
| AAPL   | Random Forest       | 0.893    |
| TSLA   | Random Forest / GBM | ~0.85+   |
| MSFT   | Ridge               | 0.955    |

---

## 📊 Evaluation Metrics

Measured by `python backend/evaluate.py` (results in `data/evaluation.json`, served by `GET /metrics`).

| Component | Method | Result |
| --- | --- | --- |
| Intent classification | 5-fold CV on 201 training examples | Acc 86.1%, F1 85.9% |
| Intent classification | 47 held-out hand-written queries | Acc 91.5%, P 92.6%, R 91.7%, F1 91.5% |
| Entity (ticker) extraction | 33 hand-written queries (8 global names, 5 with no entity) | Acc / F1 100% (small set) |
| Trend signal (SMA-14) | Walk-forward, 5-day forward direction, AAPL/MSFT/TSLA, 1,316 signals | **49.9%** vs 52.8% for an "always up" baseline |

### Can a trend signal predict direction? (`backend/trend_experiment.py`)

To try to improve the trend signal, 19 stocks (US + NSE, 10 years of daily closes) were used to test price-vs-SMA (5–50 days), SMA crossovers (5/20 … 50/200), momentum (5–120 days), mean-reversion variants and RSI, at 5- and 20-day horizons. Configurations were ranked on the first 60% of each series and scored on the last 40% (out-of-sample), against an "always predict up" baseline.

| Horizon | Best out-of-sample signal | Accuracy | Always-up baseline |
| ------- | ------------------------- | -------- | ------------------ |
| 5 days  | SMA 50/200 crossover      | 51.5%    | 54.2%              |
| 20 days | Momentum 120 days         | 52.2%    | 57.5%              |

**Result:** no signal beat the baseline at either horizon, and the original SMA-14 rule (≈51%) is typical. Stock prices rose over the period, so "always up" is hard to beat with simple price rules. So the trend feature is now described as a **descriptive** indicator (where price sits relative to its recent average), and the chatbot says so in its answers. The "~82% trend accuracy" in the dissertation could not be reproduced and should be reworded.

Also fixed: `TATAMOTORS.NS` no longer exists on Yahoo Finance after Tata Motors' 2025 demerger; "Tata / Tata Motors" now maps to `TMPV.NS`.

**Not measured automatically:** response relevance, conversation success rate and response time (they need human ratings or a live server).

> **Discrepancy with the dissertation:** the report states ~82% trend accuracy. Under the walk-forward test above, the SMA trend signal does not beat a coin flip or a naive baseline. Either the report's figure used a different definition or it should be revised. Entity results come from a small test set written by the authors, so treat them as a smoke test, not a benchmark.

------------------------- | ----------- |
| Intent Detection Accuracy | **92.4%**   |
| Entity Recognition F1     | **90.1%**   |
| Trend Prediction Accuracy | **82.7%**   |
| Sentiment Analysis F1     | **88.3%**   |
| Chatbot Success Rate      | **87.5%**   |
| Avg Response Time         | **~620 ms** |

---

## 🔑 No API Keys Required

Everything in this project uses **free, public data sources**:

| Data                   | Source                              | Requires Key? |
| ---------------------- | ----------------------------------- | ------------- |
| Stock prices & history | Yahoo Finance via `yfinance`        | ❌ No         |
| Financial news         | Yahoo Finance RSS + Google News RSS | ❌ No         |
| NLP models             | NLTK + spaCy (downloaded once)      | ❌ No         |

---

## 👤 Authors

Built as a final-year engineering project demonstrating NLP, machine learning, and real-time financial data integration.

---

_⚠️ Disclaimer: FinBot is an educational project. Nothing it says constitutes financial advice. Always do your own research before investing._
