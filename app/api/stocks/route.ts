import { NextResponse } from "next/server";

const SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM"];

interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  volume: number;
  marketCap: string;
  sector: string;
}

const STOCK_META: Record<string, { name: string; sector: string; basePrice: number; marketCap: string }> = {
  AAPL: { name: "Apple Inc.", sector: "Technology", basePrice: 198, marketCap: "3.1T" },
  GOOGL: { name: "Alphabet Inc.", sector: "Technology", basePrice: 178, marketCap: "2.2T" },
  MSFT: { name: "Microsoft Corp.", sector: "Technology", basePrice: 442, marketCap: "3.3T" },
  AMZN: { name: "Amazon.com Inc.", sector: "Consumer Cyclical", basePrice: 218, marketCap: "2.3T" },
  TSLA: { name: "Tesla Inc.", sector: "Automotive", basePrice: 352, marketCap: "1.1T" },
  META: { name: "Meta Platforms Inc.", sector: "Technology", basePrice: 612, marketCap: "1.6T" },
  NVDA: { name: "NVIDIA Corp.", sector: "Technology", basePrice: 142, marketCap: "3.5T" },
  JPM: { name: "JPMorgan Chase", sector: "Financial Services", basePrice: 268, marketCap: "690B" },
};

function generateRealisticPrice(basePrice: number): {
  price: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  volume: number;
} {
  const now = Date.now();
  const seed = Math.sin(now / 10000) * 10000;
  const noise = (Math.sin(seed) + Math.cos(seed * 0.7)) / 2;

  const changePercent = noise * 3.5;
  const change = basePrice * (changePercent / 100);
  const price = Number.parseFloat((basePrice + change).toFixed(2));
  const previousClose = basePrice;
  const open = Number.parseFloat((basePrice + change * 0.3).toFixed(2));
  const high = Number.parseFloat((Math.max(price, open) + Math.abs(change * 0.4)).toFixed(2));
  const low = Number.parseFloat((Math.min(price, open) - Math.abs(change * 0.3)).toFixed(2));
  const volume = Math.floor(20000000 + Math.random() * 80000000);

  return {
    price,
    change: Number.parseFloat(change.toFixed(2)),
    changePercent: Number.parseFloat(changePercent.toFixed(2)),
    high,
    low,
    open,
    previousClose,
    volume,
  };
}

export async function GET() {
  const stocks: StockQuote[] = SYMBOLS.map((symbol) => {
    const meta = STOCK_META[symbol];
    const priceData = generateRealisticPrice(meta.basePrice);
    return {
      symbol,
      name: meta.name,
      sector: meta.sector,
      marketCap: meta.marketCap,
      ...priceData,
    };
  });

  return NextResponse.json({ stocks, timestamp: new Date().toISOString() });
}
