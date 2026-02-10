"use client";

import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

const RANGES = [
  { label: "7D", value: "7" },
  { label: "30D", value: "30" },
  { label: "90D", value: "90" },
  { label: "1Y", value: "365" },
];

export function StockChart({ symbol }: { symbol: string }) {
  const [range, setRange] = useState("30");
  const { data, isLoading } = useSWR(
    `/api/chart?symbol=${symbol}&range=${range}`,
    fetcher,
    { refreshInterval: 10000 }
  );

  const chartData = data?.data || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card className="lg:col-span-2 bg-card border-border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold text-foreground">
              {symbol} Price History
            </CardTitle>
            <div className="flex items-center gap-1">
              {RANGES.map((r) => (
                <Button
                  key={r.value}
                  variant={range === r.value ? "default" : "ghost"}
                  size="sm"
                  className={`h-7 px-2.5 text-xs font-mono ${
                    range === r.value
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  onClick={() => setRange(r.value)}
                >
                  {r.label}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-[300px] flex items-center justify-center">
              <div className="h-4 w-32 bg-muted rounded animate-pulse" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(210, 100%, 52%)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(210, 100%, 52%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="hsl(222, 20%, 16%)"
                  vertical={false}
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: "hsl(215, 20%, 55%)" }}
                  tickFormatter={(v) => {
                    const d = new Date(v);
                    return `${d.getMonth() + 1}/${d.getDate()}`;
                  }}
                  axisLine={{ stroke: "hsl(222, 20%, 16%)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "hsl(215, 20%, 55%)" }}
                  axisLine={false}
                  tickLine={false}
                  domain={["auto", "auto"]}
                  tickFormatter={(v) => `$${v}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 47%, 8%)",
                    border: "1px solid hsl(222, 20%, 16%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(210, 40%, 96%)",
                  }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, "Price"]}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="hsl(210, 100%, 52%)"
                  strokeWidth={2}
                  fill="url(#priceGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold text-foreground">
            Volume
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-[300px] flex items-center justify-center">
              <div className="h-4 w-24 bg-muted rounded animate-pulse" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.slice(-14)}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="hsl(222, 20%, 16%)"
                  vertical={false}
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }}
                  tickFormatter={(v) => {
                    const d = new Date(v);
                    return `${d.getMonth() + 1}/${d.getDate()}`;
                  }}
                  axisLine={{ stroke: "hsl(222, 20%, 16%)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${(v / 1000000).toFixed(0)}M`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 47%, 8%)",
                    border: "1px solid hsl(222, 20%, 16%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(210, 40%, 96%)",
                  }}
                  formatter={(value: number) => [
                    `${(value / 1000000).toFixed(1)}M`,
                    "Volume",
                  ]}
                />
                <Bar
                  dataKey="volume"
                  fill="hsl(210, 100%, 52%)"
                  opacity={0.6}
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
