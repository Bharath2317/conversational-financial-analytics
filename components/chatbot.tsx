"use client";

import React from "react"

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, Clock, Target } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  metadata?: {
    intent: string;
    entities: string[];
    confidence: number;
    processingTime: number;
  };
}

const QUICK_PROMPTS = [
  "What's the price of AAPL?",
  "How is NVDA performing?",
  "Compare MSFT vs GOOGL",
  "Latest market news",
  "Market sentiment analysis",
  "Best stocks to watch",
];

export function Chatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm **FinSight AI**, your conversational financial analytics assistant powered by the OpenDialog framework and NLP pipelines.\n\nI can help you with stock prices, market trends, comparisons, news, sentiment analysis, and investment considerations.\n\nTry asking a question or use one of the quick prompts below!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content: text.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.message.content,
          metadata: data.metadata,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I apologize, but I encountered an error processing your request. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const renderContent = (content: string) => {
    const parts = content.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold text-foreground">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <Card className="bg-card border-border flex flex-col h-[600px]">
      <CardHeader className="pb-2 border-b border-border shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-foreground flex items-center gap-2">
            <div className="flex items-center justify-center h-7 w-7 rounded-lg bg-primary/10">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            FinSight AI Chat
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="text-xs bg-accent/10 text-accent border-accent/20 gap-1"
            >
              <Sparkles className="h-3 w-3" />
              OpenDialog
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div key={i}>
                <div
                  className={`flex gap-3 ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.role === "assistant" && (
                    <div className="flex items-start">
                      <div className="h-7 w-7 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                        <Bot className="h-4 w-4 text-primary" />
                      </div>
                    </div>
                  )}
                  <div
                    className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary/50 text-foreground border border-border/50"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">
                      {renderContent(msg.content)}
                    </div>
                  </div>
                  {msg.role === "user" && (
                    <div className="flex items-start">
                      <div className="h-7 w-7 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                        <User className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>
                  )}
                </div>
                {msg.metadata && (
                  <div className="flex items-center gap-3 mt-1.5 ml-10 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Target className="h-3 w-3" />
                      {msg.metadata.intent.replace("_", " ")}
                    </span>
                    <span className="flex items-center gap-1">
                      <Sparkles className="h-3 w-3" />
                      {(msg.metadata.confidence * 100).toFixed(0)}% confidence
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {msg.metadata.processingTime}ms
                    </span>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3">
                <div className="h-7 w-7 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-secondary/50 rounded-xl px-4 py-3 border border-border/50">
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-primary animate-bounce" />
                    <div
                      className="h-2 w-2 rounded-full bg-primary animate-bounce"
                      style={{ animationDelay: "0.15s" }}
                    />
                    <div
                      className="h-2 w-2 rounded-full bg-primary animate-bounce"
                      style={{ animationDelay: "0.3s" }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-3 border-t border-border shrink-0">
          <div className="flex flex-wrap gap-1.5 mb-3">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => sendMessage(prompt)}
                disabled={isLoading}
                className="text-xs px-2.5 py-1 rounded-full bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary border border-border/50 transition-colors disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about stocks, trends, sentiment..."
              disabled={isLoading}
              className="flex-1 h-10 rounded-lg bg-secondary/50 border border-border px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 disabled:opacity-50"
            />
            <Button
              type="submit"
              size="sm"
              disabled={!input.trim() || isLoading}
              className="h-10 w-10 p-0 bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <Send className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  );
}
