"use client";

import { TrendingUp, TrendingDown } from "lucide-react";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export function StockTicker() {
  const { data } = useSWR("/api/stocks", fetcher, { refreshInterval: 5000 });
  const stocks: StockQuote[] = data?.stocks || [];

  if (stocks.length === 0) {
    return (
      <div className="h-10 bg-secondary/50 flex items-center justify-center">
        <div className="h-2 w-32 rounded-full bg-muted animate-pulse" />
      </div>
    );
  }

  return (
    <div className="h-10 bg-secondary/50 border-b border-border overflow-hidden relative">
      <div className="flex items-center h-full animate-ticker whitespace-nowrap">
        {[...stocks, ...stocks].map((stock, i) => (
          <div
            key={`${stock.symbol}-${i}`}
            className="flex items-center gap-2 px-6"
          >
            <span className="font-mono text-sm font-semibold text-foreground">
              {stock.symbol}
            </span>
            <span className="font-mono text-sm text-muted-foreground">
              ${stock.price.toFixed(2)}
            </span>
            <span
              className={`flex items-center gap-0.5 font-mono text-xs font-medium ${
                stock.change >= 0
                  ? "text-accent"
                  : "text-destructive"
              }`}
            >
              {stock.change >= 0 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {stock.change >= 0 ? "+" : ""}
              {stock.changePercent.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
