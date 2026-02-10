"use client";

import { Newspaper, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

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

function getSentimentIcon(sentiment: string) {
  switch (sentiment) {
    case "positive":
      return <TrendingUp className="h-3.5 w-3.5" />;
    case "negative":
      return <TrendingDown className="h-3.5 w-3.5" />;
    default:
      return <Minus className="h-3.5 w-3.5" />;
  }
}

function getSentimentColor(sentiment: string) {
  switch (sentiment) {
    case "positive":
      return "bg-accent/10 text-accent border-accent/20";
    case "negative":
      return "bg-destructive/10 text-destructive border-destructive/20";
    default:
      return "bg-chart-4/10 text-chart-4 border-chart-4/20";
  }
}

function timeAgo(timestamp: string) {
  const diff = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function NewsSentiment() {
  const { data, isLoading } = useSWR("/api/news", fetcher, {
    refreshInterval: 30000,
  });
  const news: NewsItem[] = data?.news || [];

  const sentimentCounts = news.reduce(
    (acc, item) => {
      acc[item.sentiment]++;
      return acc;
    },
    { positive: 0, negative: 0, neutral: 0 } as Record<string, number>
  );

  const pieData = [
    { name: "Positive", value: sentimentCounts.positive, color: "hsl(160, 84%, 39%)" },
    { name: "Negative", value: sentimentCounts.negative, color: "hsl(0, 72%, 51%)" },
    { name: "Neutral", value: sentimentCounts.neutral, color: "hsl(38, 92%, 50%)" },
  ];

  const avgSentiment =
    news.length > 0
      ? news.reduce((sum, item) => sum + item.sentimentScore, 0) / news.length
      : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold text-foreground">
            Market Sentiment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 47%, 8%)",
                    border: "1px solid hsl(222, 20%, 16%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(210, 40%, 96%)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center mt-2">
              <div className="text-2xl font-bold font-mono text-foreground">
                {(avgSentiment * 100).toFixed(0)}
                <span className="text-sm text-muted-foreground font-normal">
                  /100
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Overall Sentiment Score
              </p>
            </div>
            <div className="flex items-center gap-4 mt-4">
              {pieData.map((item) => (
                <div key={item.name} className="flex items-center gap-1.5">
                  <div
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-muted-foreground">
                    {item.name} ({item.value})
                  </span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2 bg-card border-border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold text-foreground flex items-center gap-2">
              <Newspaper className="h-4 w-4 text-primary" />
              Latest Financial News
            </CardTitle>
            <span className="text-xs text-muted-foreground font-mono animate-pulse-glow">
              Live Feed
            </span>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="p-3 rounded-lg bg-secondary/50">
                  <div className="h-4 w-3/4 bg-muted rounded animate-pulse mb-2" />
                  <div className="h-3 w-1/2 bg-muted rounded animate-pulse" />
                </div>
              ))}
            </div>
          ) : (
            <ScrollArea className="h-[340px]">
              <div className="space-y-2 pr-4">
                {news.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-lg bg-secondary/30 border border-border/50 hover:border-primary/20 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3 mb-1.5">
                      <h4 className="text-sm font-medium text-foreground leading-snug">
                        {item.title}
                      </h4>
                      <Badge
                        variant="outline"
                        className={`shrink-0 text-xs gap-1 ${getSentimentColor(item.sentiment)}`}
                      >
                        {getSentimentIcon(item.sentiment)}
                        {item.sentiment}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed mb-2">
                      {item.summary}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          {item.source}
                        </span>
                        <span className="text-xs text-muted-foreground/50">
                          |
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {timeAgo(item.timestamp)}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        {item.relatedStocks.map((stock) => (
                          <span
                            key={stock}
                            className="text-xs font-mono px-1.5 py-0.5 rounded bg-primary/10 text-primary"
                          >
                            {stock}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
