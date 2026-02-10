"use client";

import { Activity, BarChart3, Bot } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-screen-2xl mx-auto px-4 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-primary/10 border border-primary/20">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground tracking-tight">
                FinSight AI
              </h1>
              <p className="text-xs text-muted-foreground -mt-0.5">
                Conversational Financial Analytics
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge
              variant="outline"
              className="gap-1.5 bg-accent/10 text-accent border-accent/20 text-xs"
            >
              <Activity className="h-3 w-3" />
              Live Data
            </Badge>
            <Badge
              variant="outline"
              className="gap-1.5 bg-primary/10 text-primary border-primary/20 text-xs"
            >
              <Bot className="h-3 w-3" />
              NLP Active
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
