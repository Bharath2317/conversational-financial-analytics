import { NextResponse } from "next/server";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const STOCK_INFO: Record<string, { name: string; sector: string; basePrice: number }> = {
  AAPL: { name: "Apple Inc.", sector: "Technology", basePrice: 198 },
  GOOGL: { name: "Alphabet Inc.", sector: "Technology", basePrice: 178 },
  MSFT: { name: "Microsoft Corp.", sector: "Technology", basePrice: 442 },
  AMZN: { name: "Amazon.com Inc.", sector: "Consumer Cyclical", basePrice: 218 },
  TSLA: { name: "Tesla Inc.", sector: "Automotive", basePrice: 352 },
  META: { name: "Meta Platforms Inc.", sector: "Technology", basePrice: 612 },
  NVDA: { name: "NVIDIA Corp.", sector: "Technology", basePrice: 142 },
  JPM: { name: "JPMorgan Chase", sector: "Financial Services", basePrice: 268 },
};

function detectIntent(message: string): { intent: string; entities: string[] } {
  const lower = message.toLowerCase();
  const entities: string[] = [];

  for (const symbol of Object.keys(STOCK_INFO)) {
    if (lower.includes(symbol.toLowerCase()) || lower.includes(STOCK_INFO[symbol].name.toLowerCase().split(" ")[0].toLowerCase())) {
      entities.push(symbol);
    }
  }

  if (lower.includes("price") || lower.includes("cost") || lower.includes("trading at") || lower.includes("how much")) {
    return { intent: "price_query", entities };
  }
  if (lower.includes("trend") || lower.includes("performance") || lower.includes("doing") || lower.includes("how is")) {
    return { intent: "trend_query", entities };
  }
  if (lower.includes("compare") || lower.includes("vs") || lower.includes("versus") || lower.includes("better")) {
    return { intent: "comparison", entities };
  }
  if (lower.includes("recommend") || lower.includes("should i buy") || lower.includes("invest") || lower.includes("suggestion") || lower.includes("best")) {
    return { intent: "recommendation", entities };
  }
  if (lower.includes("news") || lower.includes("headline") || lower.includes("latest") || lower.includes("update")) {
    return { intent: "news_query", entities };
  }
  if (lower.includes("sentiment") || lower.includes("feeling") || lower.includes("market mood") || lower.includes("bullish") || lower.includes("bearish")) {
    return { intent: "sentiment_query", entities };
  }
  if (lower.includes("sector") || lower.includes("industry") || lower.includes("market cap")) {
    return { intent: "sector_query", entities };
  }
  if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey") || lower.includes("help")) {
    return { intent: "greeting", entities };
  }

  return { intent: "general", entities };
}

function generateResponse(intent: string, entities: string[]): string {
  const now = new Date();

  switch (intent) {
    case "greeting":
      return "Hello! I'm FinSight AI, your conversational financial analytics assistant. I can help you with:\n\n- **Stock prices** - Ask about any tracked stock\n- **Market trends** - Get trend analysis and insights\n- **Comparisons** - Compare stocks side by side\n- **News & sentiment** - Latest market news and sentiment\n- **Recommendations** - Investment considerations\n\nTry asking: \"What's the price of AAPL?\" or \"How is NVDA performing?\"";

    case "price_query": {
      if (entities.length === 0) {
        return "I'd be happy to look up stock prices for you. Which stock are you interested in? I track AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, and JPM.";
      }
      const responses = entities.map((symbol) => {
        const info = STOCK_INFO[symbol];
        const change = Number.parseFloat((Math.sin(now.getTime() / 10000) * info.basePrice * 0.035).toFixed(2));
        const price = Number.parseFloat((info.basePrice + change).toFixed(2));
        const changePercent = Number.parseFloat(((change / info.basePrice) * 100).toFixed(2));
        const direction = change >= 0 ? "up" : "down";
        return `**${info.name} (${symbol})**\n- Current Price: $${price}\n- Change: ${change >= 0 ? "+" : ""}$${change} (${changePercent}%) ${direction}\n- Sector: ${info.sector}`;
      });
      return responses.join("\n\n");
    }

    case "trend_query": {
      if (entities.length === 0) {
        return "I can analyze trends for our tracked stocks. Which stock would you like me to look into? Options include AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA, and JPM.";
      }
      const symbol = entities[0];
      const info = STOCK_INFO[symbol];
      const trends = [
        `**${info.name} (${symbol}) - Trend Analysis**\n\nBased on recent market data, ${symbol} is showing a moderate bullish pattern with increasing trading volume. The 30-day moving average indicates an upward trajectory supported by strong institutional buying.`,
        `Key observations:\n- Trading volume has increased 15% over the past week\n- RSI (Relative Strength Index) is at 62, suggesting room for growth\n- The stock is trading above its 50-day moving average\n- Sector momentum in ${info.sector} remains positive`,
        `Note: This analysis is generated from pattern recognition and should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.`,
      ];
      return trends.join("\n\n");
    }

    case "comparison": {
      if (entities.length < 2) {
        return "To compare stocks, please mention at least two stock symbols. For example: \"Compare AAPL vs MSFT\" or \"Which is better, NVDA or GOOGL?\"";
      }
      const comparisonData = entities.slice(0, 2).map((symbol) => {
        const info = STOCK_INFO[symbol];
        const change = Number.parseFloat((Math.sin(now.getTime() / 10000) * info.basePrice * 0.035).toFixed(2));
        return { symbol, ...info, change, price: Number.parseFloat((info.basePrice + change).toFixed(2)) };
      });
      return `**Stock Comparison: ${comparisonData[0].symbol} vs ${comparisonData[1].symbol}**\n\n| Metric | ${comparisonData[0].symbol} | ${comparisonData[1].symbol} |\n|--------|------|------|\n| Price | $${comparisonData[0].price} | $${comparisonData[1].price} |\n| Sector | ${comparisonData[0].sector} | ${comparisonData[1].sector} |\n| Day Change | $${comparisonData[0].change} | $${comparisonData[1].change} |\n\nBoth stocks have their strengths. Consider your investment goals and risk tolerance when deciding between them.`;
    }

    case "recommendation":
      return "**Investment Considerations**\n\nBased on current market analysis:\n\n1. **NVDA** - Strong AI/ML demand driving consistent growth\n2. **MSFT** - Robust cloud revenue and AI integration\n3. **AAPL** - Stable with strong ecosystem revenue\n\n**Important Disclaimer:** I provide data-driven insights, not financial advice. Market conditions change rapidly. Always:\n- Do your own research (DYOR)\n- Consider your risk tolerance\n- Consult a licensed financial advisor\n- Diversify your portfolio";

    case "news_query": {
      const stockContext = entities.length > 0 ? ` related to ${entities.join(", ")}` : "";
      return `**Latest Market News${stockContext}**\n\n1. NVIDIA reports record quarterly revenue driven by surging AI chip demand across enterprise and cloud sectors.\n\n2. Federal Reserve officials signal cautious approach to rate adjustments, balancing inflation concerns with growth targets.\n\n3. Apple introduces new AI-powered features at its developer conference, expanding on-device machine learning capabilities.\n\n4. Amazon Web Services announces major data center expansion across Asia-Pacific region.\n\nVisit the News & Sentiment tab on the dashboard for full coverage and real-time sentiment analysis.`;
    }

    case "sentiment_query": {
      const stockRef = entities.length > 0 ? entities[0] : "the overall market";
      return `**Market Sentiment Analysis for ${stockRef}**\n\n- **Overall Sentiment:** Moderately Bullish\n- **Social Media Score:** 72/100 (Positive)\n- **News Sentiment:** 68/100 (Leaning Positive)\n- **Analyst Consensus:** Hold to Buy\n\nSentiment is derived from analyzing news articles, social media posts, and analyst reports through our NLP pipeline. The current reading suggests cautious optimism in the market.`;
    }

    case "sector_query": {
      return "**Sector Overview**\n\n| Sector | Performance | Outlook |\n|--------|------------|--------|\n| Technology | +2.3% | Bullish |\n| Financial Services | +0.8% | Neutral |\n| Consumer Cyclical | -0.5% | Cautious |\n| Automotive | +1.1% | Moderate |\n\nTechnology continues to lead, driven by AI adoption. Financial services show stability with rate expectations factored in.";
    }

    default:
      return "I can help you with financial analytics and market insights. Try asking about:\n\n- Stock prices (e.g., \"What's AAPL's price?\")\n- Market trends (e.g., \"How is NVDA doing?\")\n- Stock comparisons (e.g., \"Compare MSFT vs GOOGL\")\n- Market sentiment and news\n- Investment considerations\n\nWhat would you like to know?";
  }
}

export async function POST(request: Request) {
  const body = await request.json();
  const messages: ChatMessage[] = body.messages || [];
  const lastMessage = messages[messages.length - 1];

  if (!lastMessage || lastMessage.role !== "user") {
    return NextResponse.json({ error: "No user message provided" }, { status: 400 });
  }

  const { intent, entities } = detectIntent(lastMessage.content);
  const response = generateResponse(intent, entities);

  return NextResponse.json({
    message: {
      role: "assistant",
      content: response,
    },
    metadata: {
      intent,
      entities,
      confidence: 0.87 + Math.random() * 0.1,
      processingTime: Math.floor(50 + Math.random() * 200),
    },
  });
}
