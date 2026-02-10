import { type NextRequest, NextResponse } from "next/server";

const BASE_PRICES: Record<string, number> = {
  AAPL: 198,
  GOOGL: 178,
  MSFT: 442,
  AMZN: 218,
  TSLA: 352,
  META: 612,
  NVDA: 142,
  JPM: 268,
};

function generateHistoricalData(symbol: string, days: number) {
  const basePrice = BASE_PRICES[symbol] || 150;
  const data = [];
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const trend = Math.sin(i / 10) * basePrice * 0.03;
    const noise = (Math.sin(i * 7.3) + Math.cos(i * 13.1)) * basePrice * 0.015;
    const price = Number.parseFloat((basePrice + trend + noise).toFixed(2));
    const volume = Math.floor(30000000 + Math.sin(i * 3.7) * 20000000);

    data.push({
      date: date.toISOString().split("T")[0],
      price,
      volume,
      high: Number.parseFloat((price + Math.abs(noise) * 0.8).toFixed(2)),
      low: Number.parseFloat((price - Math.abs(noise) * 0.6).toFixed(2)),
    });
  }

  return data;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get("symbol") || "AAPL";
  const range = searchParams.get("range") || "30";
  const days = Number.parseInt(range, 10);

  const data = generateHistoricalData(symbol, days);

  return NextResponse.json({ symbol, data, range: days });
}
