"use client";

import { useState, useMemo } from "react";
import { TrendingUp, TrendingDown, BarChart2, Search, Filter } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
  exchange: string;
}

const SECTORS = [
  "All",
  "Banking",
  "IT",
  "FMCG",
  "Pharma",
  "Oil & Gas",
  "Automobile",
  "Metals",
  "Power",
  "Infrastructure",
  "Insurance",
  "Financial Services",
  "Telecom",
  "Conglomerate",
  "Mining",
  "Healthcare",
  "Consumer Goods",
  "Cement",
];

export function StockCards({
  onSelectStock,
  selectedStock,
}: {
  onSelectStock: (symbol: string) => void;
  selectedStock: string;
}) {
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("All");
  const [showAll, setShowAll] = useState(false);

  const { data, isLoading } = useSWR("/api/stocks", fetcher, {
    refreshInterval: 5000,
  });
  const stocks: StockQuote[] = data?.stocks || [];

  const filtered = useMemo(() => {
    return stocks.filter((s) => {
      const matchSearch =
        search === "" ||
        s.symbol.toLowerCase().includes(search.toLowerCase()) ||
        s.name.toLowerCase().includes(search.toLowerCase());
      const matchSector = sector === "All" || s.sector === sector;
      return matchSearch && matchSector;
    });
  }, [stocks, search, sector]);

  const displayed = showAll ? filtered : filtered.slice(0, 12);

  const gainers = useMemo(() => [...stocks].sort((a, b) => b.changePercent - a.changePercent).slice(0, 5), [stocks]);
  const losers = useMemo(() => [...stocks].sort((a, b) => a.changePercent - b.changePercent).slice(0, 5), [stocks]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {Array.from({ length: 12 }).map((_, i) => (
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
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Top Gainers / Losers Strip */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <Card className="bg-card border-border">
          <CardContent className="p-3">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-accent" />
              <span className="text-sm font-semibold text-foreground">Top Gainers</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {gainers.map((s) => (
                <button
                  type="button"
                  key={s.symbol}
                  onClick={() => onSelectStock(s.symbol)}
                  className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-accent/5 border border-accent/10 hover:bg-accent/10 transition-colors"
                >
                  <span className="font-mono text-xs font-semibold text-foreground">{s.symbol}</span>
                  <span className="font-mono text-xs text-accent">+{s.changePercent.toFixed(2)}%</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-3">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4 text-destructive" />
              <span className="text-sm font-semibold text-foreground">Top Losers</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {losers.map((s) => (
                <button
                  type="button"
                  key={s.symbol}
                  onClick={() => onSelectStock(s.symbol)}
                  className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-destructive/5 border border-destructive/10 hover:bg-destructive/10 transition-colors"
                >
                  <span className="font-mono text-xs font-semibold text-foreground">{s.symbol}</span>
                  <span className="font-mono text-xs text-destructive">{s.changePercent.toFixed(2)}%</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search 50 stocks by name or symbol..."
            className="w-full h-9 pl-9 pr-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50"
          />
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          <Filter className="h-4 w-4 text-muted-foreground shrink-0" />
          {SECTORS.slice(0, 8).map((s) => (
            <button
              type="button"
              key={s}
              onClick={() => setSector(s)}
              className={`text-xs px-2 py-1 rounded-md border transition-colors ${
                sector === s
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-secondary/50 text-muted-foreground border-border hover:text-foreground"
              }`}
            >
              {s}
            </button>
          ))}
          {SECTORS.length > 8 && (
            <select
              value={SECTORS.slice(8).includes(sector) ? sector : ""}
              onChange={(e) => e.target.value && setSector(e.target.value)}
              className="text-xs px-2 py-1 rounded-md border border-border bg-secondary/50 text-muted-foreground focus:outline-none"
            >
              <option value="">More...</option>
              {SECTORS.slice(8).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Showing {displayed.length} of {filtered.length} stocks
          {sector !== "All" && <span> in <Badge variant="outline" className="ml-1 text-xs">{sector}</Badge></span>}
        </p>
      </div>

      {/* Stock Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {displayed.map((stock) => {
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
                    <Badge variant="outline" className="text-[10px] px-1 py-0 h-4 border-border text-muted-foreground">
                      {stock.exchange}
                    </Badge>
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
                <p className="text-xs text-muted-foreground truncate mb-1">{stock.name}</p>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-lg font-bold font-mono text-foreground">
                    {"Rs "}{stock.price.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                    Vol: {(stock.volume / 100000).toFixed(1)}L
                  </span>
                  <span className="mx-1">|</span>
                  <span className="font-mono text-[10px]">{stock.sector}</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {!showAll && filtered.length > 12 && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAll(true)}
            className="text-xs bg-transparent"
          >
            Show all {filtered.length} stocks
          </Button>
        </div>
      )}
      {showAll && filtered.length > 12 && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAll(false)}
            className="text-xs bg-transparent"
          >
            Show less
          </Button>
        </div>
      )}
    </div>
  );
}
