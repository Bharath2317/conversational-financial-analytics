"""
news_fetcher.py — Real Financial News via Free RSS Feeds (No API Key Required)

Sources:
  • Yahoo Finance RSS  — per-ticker headlines
  • Google News RSS    — company-specific news search
  • MarketWatch RSS    — market news

Returns structured news items with title, source, link, published date.
"""

import feedparser
import re
import datetime
from urllib.parse import quote
from sentiment_analysis import analyze_sentiment


# ─── RSS Feed Sources ──────────────────────────────────────────────────────────
def _yahoo_rss(symbol: str) -> str:
    return f"https://finance.yahoo.com/rss/headline?s={symbol}"

def _google_news_rss(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(query + ' stock')}&hl=en-US&gl=US&ceid=US:en"

def _marketwatch_rss() -> str:
    return "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"


# ─── Parser ────────────────────────────────────────────────────────────────────
def _parse_feed(url: str, limit: int = 5) -> list[dict]:
    """Fetch and parse an RSS feed, returning clean news items."""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            # Clean HTML tags from summary
            summary = re.sub(r'<[^>]+>', '', getattr(entry, 'summary', ''))
            published = getattr(entry, 'published', '')
            try:
                pub_struct = entry.get('published_parsed')
                if pub_struct:
                    published = datetime.datetime(*pub_struct[:6]).strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass

            items.append({
                "title"    : getattr(entry, 'title', 'No title'),
                "summary"  : summary[:200] if summary else "",
                "link"     : getattr(entry, 'link', ''),
                "source"   : feed.feed.get('title', 'Unknown'),
                "published": published,
            })
        return items
    except Exception as e:
        return []


# ─── Public API ────────────────────────────────────────────────────────────────
def fetch_news(symbol: str, company_name: str = "", limit: int = 6) -> dict:
    """
    Fetch real financial news headlines for a ticker symbol.

    Args:
        symbol       (str): Ticker, e.g. "AAPL"
        company_name (str): Full name for broader search, e.g. "Apple"
        limit        (int): Max articles to return

    Returns:
        dict: {
            "symbol"   : str,
            "articles" : [ {title, summary, link, source, published, sentiment} ],
            "overall_sentiment": { sentiment, score, ... },
            "total"    : int
        }
    """
    all_articles = []

    # Source 1 — Yahoo Finance (most relevant per ticker)
    yahoo = _parse_feed(_yahoo_rss(symbol), limit=limit)
    all_articles.extend(yahoo)

    # Source 2 — Google News (broader coverage)
    query = company_name if company_name else symbol
    gnews = _parse_feed(_google_news_rss(query), limit=limit)
    # Deduplicate by title
    seen_titles = {a["title"] for a in all_articles}
    for a in gnews:
        if a["title"] not in seen_titles:
            all_articles.append(a)
            seen_titles.add(a["title"])

    # Limit total
    all_articles = all_articles[:limit]

    # Run sentiment on each headline
    for article in all_articles:
        text = f"{article['title']}. {article['summary']}"
        article["sentiment"] = analyze_sentiment(text)

    # Compute overall sentiment (average of all scores)
    if all_articles:
        avg_score = sum(a["sentiment"]["score"] for a in all_articles) / len(all_articles)
        if avg_score >= 0.05:
            overall_label = "positive"
        elif avg_score <= -0.05:
            overall_label = "negative"
        else:
            overall_label = "neutral"
        overall = {
            "sentiment": overall_label,
            "score"    : round(avg_score, 4),
        }
    else:
        overall = {"sentiment": "neutral", "score": 0.0}

    return {
        "symbol"            : symbol.upper(),
        "articles"          : all_articles,
        "overall_sentiment" : overall,
        "total"             : len(all_articles),
    }


# ─── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    ICONS = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}

    for sym, name in [("AAPL", "Apple"), ("TSLA", "Tesla"), ("NVDA", "Nvidia")]:
        print(f"\n{'═'*65}")
        print(f"  📰 News Feed — {sym} ({name})")
        print(f"{'═'*65}")
        result = fetch_news(sym, name, limit=4)
        overall = result["overall_sentiment"]
        icon = ICONS.get(overall["sentiment"], "🟡")
        print(f"  Overall Sentiment: {icon} {overall['sentiment'].upper()} (score: {overall['score']:+.4f})")
        print(f"  Articles fetched : {result['total']}\n")
        for i, a in enumerate(result["articles"], 1):
            sent = a["sentiment"]
            s_icon = ICONS.get(sent["sentiment"], "🟡")
            print(f"  [{i}] {a['title'][:80]}")
            print(f"       Source: {a['source']}  |  {a['published']}")
            print(f"       Sentiment: {s_icon} {sent['sentiment']} ({sent['score']:+.3f})\n")
