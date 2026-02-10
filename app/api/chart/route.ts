import { type NextRequest, NextResponse } from "next/server";
import { INDIAN_STOCKS } from "@/app/api/stocks/route";

function generateHistoricalData(symbol: string, days: number) {
  const meta = INDIAN_STOCKS[symbol];
  const basePrice = meta?.basePrice || 1000;
  const data = [];
  const now = new Date();
  const symbolSeed = symbol.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const trend = Math.sin((i + symbolSeed) / 10) * basePrice * 0.03;
    const noise = (Math.sin(i * 7.3 + symbolSeed) + Math.cos(i * 13.1 + symbolSeed)) * basePrice * 0.015;
    const price = Number.parseFloat((basePrice + trend + noise).toFixed(2));
    const volume = Math.floor(3000000 + Math.sin(i * 3.7 + symbolSeed) * 2000000);

    data.push({
      date: date.toISOString().split("T")[0],
      price,
      volume: Math.abs(volume),
      high: Number.parseFloat((price + Math.abs(noise) * 0.8).toFixed(2)),
      low: Number.parseFloat((price - Math.abs(noise) * 0.6).toFixed(2)),
    });
  }

  return data;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const symbol = searchParams.get("symbol") || "RELIANCE";
  const range = searchParams.get("range") || "30";
  const days = Number.parseInt(range, 10);

  const data = generateHistoricalData(symbol, days);

  return NextResponse.json({ symbol, data, range: days });
}
