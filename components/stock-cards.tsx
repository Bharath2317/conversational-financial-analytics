"use client";

import { TrendingUp, TrendingDown, BarChart2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  volume: number;
  marketCap: string;
  sector: string;
}

export function StockCards({
  onSelectStock,
  selectedStock,
}: {
  onSelectStock: (symbol: string) => void;
  selectedStock: string;
}) {
  const { data, isLoading } = useSWR("/api/stocks", fetcher, {
    refreshInterval: 5000,
  });
  const stocks: StockQuote[] = data?.stocks || [];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <Card key={i} className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="h-4 w-16 bg-muted rounded animate-pulse" />
                <div className="h-4 w-12 bg-muted rounded animate-pulse" />
              </div>
              <div className="h-6 w-24 bg-muted rounded animate-pulse mb-2" />
              <div className="h-3 w-20 bg-muted rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {stocks.map((stock) => {
        const isPositive = stock.change >= 0;
        const isSelected = selectedStock === stock.symbol;
        return (
          <Card
            key={stock.symbol}
            className={`bg-card border cursor-pointer transition-all hover:border-primary/40 ${
              isSelected
                ? "border-primary/60 ring-1 ring-primary/20"
                : "border-border"
            }`}
            onClick={() => onSelectStock(stock.symbol)}
          >
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm font-bold text-foreground">
                    {stock.symbol}
                  </span>
                  <span className="text-xs text-muted-foreground truncate max-w-[80px]">
                    {stock.sector}
                  </span>
                </div>
                <div
                  className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-medium ${
                    isPositive
                      ? "bg-accent/10 text-accent"
                      : "bg-destructive/10 text-destructive"
                  }`}
                >
                  {isPositive ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {isPositive ? "+" : ""}
                  {stock.changePercent.toFixed(2)}%
                </div>
              </div>
              <div className="flex items-baseline gap-2 mb-1">
                <span className="text-xl font-bold font-mono text-foreground">
                  ${stock.price.toFixed(2)}
                </span>
                <span
                  className={`text-xs font-mono ${
                    isPositive ? "text-accent" : "text-destructive"
                  }`}
                >
                  {isPositive ? "+" : ""}
                  {stock.change.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <BarChart2 className="h-3 w-3" />
                <span className="font-mono">
                  Vol: {(stock.volume / 1000000).toFixed(1)}M
                </span>
                <span className="mx-1">|</span>
                <span className="font-mono">Cap: {stock.marketCap}</span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
