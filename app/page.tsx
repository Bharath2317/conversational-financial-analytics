"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, MessageSquare, Newspaper, Brain } from "lucide-react";
import { DashboardHeader } from "@/components/dashboard-header";
import { StockTicker } from "@/components/stock-ticker";
import { StockCards } from "@/components/stock-cards";
import { StockChart } from "@/components/stock-chart";
import { NewsSentiment } from "@/components/news-sentiment";
import { Chatbot } from "@/components/chatbot";
import { NlpMetrics } from "@/components/nlp-metrics";

export default function Home() {
  const [selectedStock, setSelectedStock] = useState("AAPL");

  return (
    <div className="min-h-screen bg-background">
      <StockTicker />
      <DashboardHeader />

      <main className="max-w-screen-2xl mx-auto px-4 lg:px-8 py-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground tracking-tight text-balance">
            Conversational Financial Analytics
          </h2>
          <p className="text-sm text-muted-foreground mt-1 max-w-2xl leading-relaxed">
            Real-time market data, NLP-powered sentiment analysis, and
            conversational AI built with the OpenDialog framework. Ask questions
            in natural language to explore financial insights.
          </p>
        </div>

        <Tabs defaultValue="dashboard" className="space-y-4">
          <TabsList className="bg-secondary/50 border border-border">
            <TabsTrigger
              value="dashboard"
              className="gap-1.5 data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
            >
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Market Dashboard</span>
              <span className="sm:hidden">Markets</span>
            </TabsTrigger>
            <TabsTrigger
              value="news"
              className="gap-1.5 data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
            >
              <Newspaper className="h-4 w-4" />
              <span className="hidden sm:inline">{"News & Sentiment"}</span>
              <span className="sm:hidden">News</span>
            </TabsTrigger>
            <TabsTrigger
              value="chat"
              className="gap-1.5 data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
            >
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">AI Assistant</span>
              <span className="sm:hidden">Chat</span>
            </TabsTrigger>
            <TabsTrigger
              value="nlp"
              className="gap-1.5 data-[state=active]:bg-card data-[state=active]:text-foreground text-muted-foreground"
            >
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">NLP Pipeline</span>
              <span className="sm:hidden">NLP</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-4">
            <StockCards
              onSelectStock={setSelectedStock}
              selectedStock={selectedStock}
            />
            <StockChart symbol={selectedStock} />
          </TabsContent>

          <TabsContent value="news">
            <NewsSentiment />
          </TabsContent>

          <TabsContent value="chat">
            <div className="max-w-4xl mx-auto">
              <Chatbot />
            </div>
          </TabsContent>

          <TabsContent value="nlp">
            <NlpMetrics />
          </TabsContent>
        </Tabs>

        <footer className="mt-12 pt-6 border-t border-border">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-foreground">
                FinSight AI
              </span>
              <span className="text-xs text-muted-foreground">
                Conversational Financial Analytics Platform
              </span>
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Built with OpenDialog Framework and NLP Pipelines. Data is
              simulated for demonstration purposes. Not financial advice.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
