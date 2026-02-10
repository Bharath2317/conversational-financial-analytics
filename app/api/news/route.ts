import { NextResponse } from "next/server";

interface NewsItem {
  id: string;
  title: string;
  source: string;
  sentiment: "positive" | "negative" | "neutral";
  sentimentScore: number;
  timestamp: string;
  summary: string;
  relatedStocks: string[];
}

const NEWS_TEMPLATES: Omit<NewsItem, "id" | "timestamp">[] = [
  {
    title: "NVIDIA Reports Record Revenue Driven by AI Chip Demand",
    source: "Reuters",
    sentiment: "positive",
    sentimentScore: 0.92,
    summary: "NVIDIA's quarterly earnings surpassed expectations as the AI chip market continues to expand rapidly across enterprise and cloud computing sectors.",
    relatedStocks: ["NVDA", "MSFT", "GOOGL"],
  },
  {
    title: "Federal Reserve Signals Potential Rate Adjustment in Q2",
    source: "Bloomberg",
    sentiment: "neutral",
    sentimentScore: 0.51,
    summary: "The Federal Reserve indicated a possible change in interest rates, citing balanced risks between inflation control and economic growth.",
    relatedStocks: ["JPM", "AAPL", "MSFT"],
  },
  {
    title: "Tesla Faces Supply Chain Challenges in European Markets",
    source: "Financial Times",
    sentiment: "negative",
    sentimentScore: 0.22,
    summary: "Tesla is navigating supply chain disruptions affecting its European manufacturing operations, potentially impacting delivery targets.",
    relatedStocks: ["TSLA"],
  },
  {
    title: "Apple Unveils New AI-Powered Features at Developer Conference",
    source: "CNBC",
    sentiment: "positive",
    sentimentScore: 0.85,
    summary: "Apple introduced a suite of AI-powered features across its ecosystem, including enhanced Siri capabilities and on-device machine learning.",
    relatedStocks: ["AAPL", "GOOGL"],
  },
  {
    title: "Amazon Web Services Expands Data Center Operations in Asia",
    source: "Wall Street Journal",
    sentiment: "positive",
    sentimentScore: 0.78,
    summary: "AWS announced plans to build new data centers across Asia-Pacific, reinforcing its position in the cloud computing market.",
    relatedStocks: ["AMZN", "MSFT", "GOOGL"],
  },
  {
    title: "Meta Platforms Reports Surge in Ad Revenue from Reels",
    source: "MarketWatch",
    sentiment: "positive",
    sentimentScore: 0.88,
    summary: "Meta saw significant growth in advertising revenue driven by its Reels short-form video platform, exceeding analyst projections.",
    relatedStocks: ["META"],
  },
  {
    title: "Global Semiconductor Shortage Shows Signs of Easing",
    source: "Nikkei Asia",
    sentiment: "neutral",
    sentimentScore: 0.55,
    summary: "Industry analysts note improving semiconductor supply conditions, though certain high-end chip categories remain constrained.",
    relatedStocks: ["NVDA", "AAPL", "TSLA"],
  },
  {
    title: "JPMorgan Warns of Increased Market Volatility Ahead",
    source: "Bloomberg",
    sentiment: "negative",
    sentimentScore: 0.3,
    summary: "JPMorgan's chief strategist cautioned investors about potential market turbulence driven by geopolitical tensions and economic uncertainty.",
    relatedStocks: ["JPM", "AMZN", "MSFT"],
  },
  {
    title: "Microsoft Azure Revenue Grows 29% Year-Over-Year",
    source: "TechCrunch",
    sentiment: "positive",
    sentimentScore: 0.91,
    summary: "Microsoft's cloud platform Azure continued its strong growth trajectory, driven by enterprise AI adoption and hybrid cloud solutions.",
    relatedStocks: ["MSFT", "GOOGL", "AMZN"],
  },
  {
    title: "Alphabet DeepMind Achieves Breakthrough in Protein Folding",
    source: "Nature",
    sentiment: "positive",
    sentimentScore: 0.82,
    summary: "DeepMind's latest model achieves unprecedented accuracy in protein structure prediction, opening new possibilities in drug discovery.",
    relatedStocks: ["GOOGL"],
  },
];

export async function GET() {
  const now = new Date();
  const news: NewsItem[] = NEWS_TEMPLATES.map((template, i) => ({
    ...template,
    id: `news-${i}-${now.getTime()}`,
    timestamp: new Date(now.getTime() - i * 1800000).toISOString(),
  }));

  return NextResponse.json({ news, timestamp: now.toISOString() });
}
