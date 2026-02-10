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
    title: "Reliance Industries Reports Strong Q3 Earnings, Jio Subscriber Base Crosses 500M",
    source: "Economic Times",
    sentiment: "positive",
    sentimentScore: 0.92,
    summary: "Reliance Industries delivered robust quarterly results with Jio Platforms driving growth. Retail business also showed double-digit expansion across segments.",
    relatedStocks: ["RELIANCE", "BHARTIARTL"],
  },
  {
    title: "RBI Maintains Repo Rate, Signals Accommodative Stance Amid Inflation Concerns",
    source: "Mint",
    sentiment: "neutral",
    sentimentScore: 0.51,
    summary: "The Reserve Bank of India kept the benchmark repo rate unchanged at 6.5%, signaling a balanced approach between inflation control and economic growth support.",
    relatedStocks: ["HDFCBANK", "SBIN", "ICICIBANK", "KOTAKBANK"],
  },
  {
    title: "Tata Motors EV Sales Decline 12% as Competition Intensifies in Domestic Market",
    source: "Business Standard",
    sentiment: "negative",
    sentimentScore: 0.22,
    summary: "Tata Motors saw a dip in electric vehicle sales as Mahindra and Hyundai ramp up their EV offerings, intensifying competition in the Indian market.",
    relatedStocks: ["TATAMOTORS", "MARUTI", "EICHERMOT"],
  },
  {
    title: "TCS Bags $2.5 Billion Deal from European Banking Major for Digital Transformation",
    source: "Moneycontrol",
    sentiment: "positive",
    sentimentScore: 0.89,
    summary: "TCS secured one of its largest deals in recent quarters, a multi-year digital transformation contract with a top European bank covering cloud, AI, and cybersecurity.",
    relatedStocks: ["TCS", "INFY", "WIPRO", "HCLTECH"],
  },
  {
    title: "Adani Group Announces Rs 50,000 Cr Investment in Green Energy Projects",
    source: "NDTV Profit",
    sentiment: "positive",
    sentimentScore: 0.78,
    summary: "Adani Group unveiled plans to invest in solar and wind energy projects across Gujarat and Rajasthan, targeting 45 GW renewable capacity by 2030.",
    relatedStocks: ["ADANIENT", "ADANIPORTS", "NTPC", "POWERGRID"],
  },
  {
    title: "HDFC Bank Net Profit Rises 20% YoY as Credit Growth Remains Strong",
    source: "Financial Express",
    sentiment: "positive",
    sentimentScore: 0.88,
    summary: "HDFC Bank reported strong quarterly results with net profit growth of 20% year-over-year, driven by robust retail and corporate lending growth.",
    relatedStocks: ["HDFCBANK", "ICICIBANK", "AXISBANK"],
  },
  {
    title: "IT Sector Faces Headwinds as US Clients Delay Discretionary Spending",
    source: "Economic Times",
    sentiment: "negative",
    sentimentScore: 0.28,
    summary: "Indian IT companies are facing a challenging environment as US and European clients continue to defer discretionary technology spending amid macro uncertainty.",
    relatedStocks: ["INFY", "TCS", "WIPRO", "HCLTECH", "TECHM"],
  },
  {
    title: "Sun Pharma Gets US FDA Approval for New Specialty Drug, Stock Surges",
    source: "Business Today",
    sentiment: "positive",
    sentimentScore: 0.85,
    summary: "Sun Pharmaceutical received FDA approval for its new specialty dermatology drug, expected to generate $500M+ annual revenue at peak sales.",
    relatedStocks: ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB"],
  },
  {
    title: "Sensex Crosses 85,000 Mark for First Time as FII Inflows Surge",
    source: "Mint",
    sentiment: "positive",
    sentimentScore: 0.91,
    summary: "The BSE Sensex breached the historic 85,000 level as foreign institutional investors pumped in over Rs 15,000 crore in the past week, led by banking and IT stocks.",
    relatedStocks: ["RELIANCE", "TCS", "HDFCBANK", "INFY"],
  },
  {
    title: "Maruti Suzuki Faces Production Halt at Manesar Plant Due to Supply Issues",
    source: "Auto Car India",
    sentiment: "negative",
    sentimentScore: 0.25,
    summary: "Maruti Suzuki temporarily halted production at its Manesar facility due to semiconductor shortages, affecting deliveries of popular models including Brezza and Fronx.",
    relatedStocks: ["MARUTI", "TATAMOTORS", "BAJAJ_AUTO"],
  },
  {
    title: "Bharti Airtel 5G Coverage Reaches 500 Cities, ARPU Continues Upward Trend",
    source: "Telecom Talk",
    sentiment: "positive",
    sentimentScore: 0.82,
    summary: "Bharti Airtel expanded its 5G network to 500 cities with average revenue per user (ARPU) rising to Rs 233, supported by premium plan adoption.",
    relatedStocks: ["BHARTIARTL", "RELIANCE"],
  },
  {
    title: "Coal India Output Rises 8% in January, Meets Government Production Targets",
    source: "Reuters India",
    sentiment: "positive",
    sentimentScore: 0.72,
    summary: "Coal India achieved an 8% year-over-year increase in coal production, meeting the government's ambitious targets amid rising power demand across the country.",
    relatedStocks: ["COALINDIA", "NTPC", "POWERGRID"],
  },
  {
    title: "Vedanta Announces Demerger Plans to Unlock Value Across Business Verticals",
    source: "Moneycontrol",
    sentiment: "neutral",
    sentimentScore: 0.55,
    summary: "Vedanta Limited confirmed plans to demerge its business into separate listed entities for metals, oil & gas, and semiconductors to unlock shareholder value.",
    relatedStocks: ["VEDL", "HINDALCO", "JSWSTEEL", "TATASTEEL"],
  },
  {
    title: "Asian Paints Margin Under Pressure as Crude Oil Prices Rise Sharply",
    source: "Business Standard",
    sentiment: "negative",
    sentimentScore: 0.3,
    summary: "Asian Paints faces margin headwinds as raw material costs linked to crude oil prices surge, potentially impacting profitability in the coming quarters.",
    relatedStocks: ["ASIANPAINT", "HINDUNILVR", "NESTLEIND"],
  },
  {
    title: "Titan Company Sees 25% Growth in Jewellery Division During Festival Season",
    source: "NDTV Profit",
    sentiment: "positive",
    sentimentScore: 0.86,
    summary: "Titan Company reported exceptional growth in its jewellery segment during the festive season, with Tanishq brand driving strong same-store sales growth.",
    relatedStocks: ["TITAN", "DABUR", "BRITANNIA"],
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
