"use client";

import {
  Brain,
  MessageSquare,
  Target,
  Zap,
  Shield,
  Activity,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

const METRICS = [
  {
    name: "Intent Classification",
    accuracy: 92,
    precision: 91,
    recall: 93,
    f1: 92,
    icon: Target,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    name: "Entity Extraction",
    accuracy: 90,
    precision: 89,
    recall: 91,
    f1: 90,
    icon: Brain,
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
  {
    name: "Market Prediction",
    accuracy: 82,
    precision: 80,
    recall: 83,
    f1: 82,
    icon: Activity,
    color: "text-chart-4",
    bgColor: "bg-chart-4/10",
  },
  {
    name: "Response Relevance",
    accuracy: 81,
    precision: 90,
    recall: 92,
    f1: 81,
    icon: MessageSquare,
    color: "text-chart-5",
    bgColor: "bg-chart-5/10",
  },
  {
    name: "Financial Analysis",
    accuracy: 91,
    precision: 90,
    recall: 92,
    f1: 91,
    icon: Zap,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    name: "Conversation Success",
    accuracy: 87,
    precision: 86,
    recall: 88,
    f1: 87,
    icon: Shield,
    color: "text-accent",
    bgColor: "bg-accent/10",
  },
];

const BAR_DATA = METRICS.map((m) => ({
  name: m.name.split(" ")[0],
  Accuracy: m.accuracy,
  Precision: m.precision,
  Recall: m.recall,
  F1: m.f1,
}));

const RADAR_DATA = METRICS.map((m) => ({
  subject: m.name.split(" ")[0],
  score: m.f1,
  fullMark: 100,
}));

const PIPELINE_STEPS = [
  {
    step: "1",
    title: "Text Preprocessing",
    description: "Tokenization, stopword removal, and lemmatization of raw financial text data",
  },
  {
    step: "2",
    title: "Entity Recognition",
    description: "Detect company names, stock symbols, and financial metrics from user queries",
  },
  {
    step: "3",
    title: "Intent Detection",
    description: "Classify user intent - price query, trend analysis, comparison, or recommendation",
  },
  {
    step: "4",
    title: "Sentiment Analysis",
    description: "Analyze news and social media sentiment using NLP scoring models",
  },
  {
    step: "5",
    title: "Response Generation",
    description: "Generate contextual responses using OpenDialog multi-turn conversation framework",
  },
];

export function NlpMetrics() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {METRICS.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.name} className="bg-card border-border">
              <CardContent className="p-3">
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className={`h-7 w-7 rounded-lg ${metric.bgColor} flex items-center justify-center`}
                  >
                    <Icon className={`h-3.5 w-3.5 ${metric.color}`} />
                  </div>
                </div>
                <div className="text-2xl font-bold font-mono text-foreground">
                  {metric.f1}%
                </div>
                <p className="text-xs text-muted-foreground mt-0.5 leading-tight">
                  {metric.name}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold text-foreground">
              Performance Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={BAR_DATA} barGap={2}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="hsl(222, 20%, 16%)"
                  vertical={false}
                />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }}
                  axisLine={{ stroke: "hsl(222, 20%, 16%)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }}
                  axisLine={false}
                  tickLine={false}
                  domain={[60, 100]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 47%, 8%)",
                    border: "1px solid hsl(222, 20%, 16%)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(210, 40%, 96%)",
                  }}
                />
                <Bar dataKey="Accuracy" fill="hsl(210, 100%, 52%)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Precision" fill="hsl(160, 84%, 39%)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Recall" fill="hsl(38, 92%, 50%)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="F1" fill="hsl(270, 60%, 55%)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold text-foreground">
              F1-Score Radar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={RADAR_DATA}>
                <PolarGrid stroke="hsl(222, 20%, 16%)" />
                <PolarAngleAxis
                  dataKey="subject"
                  tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  tick={{ fontSize: 9, fill: "hsl(215, 20%, 55%)" }}
                />
                <Radar
                  name="F1-Score"
                  dataKey="score"
                  stroke="hsl(210, 100%, 52%)"
                  fill="hsl(210, 100%, 52%)"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold text-foreground flex items-center gap-2">
            <Brain className="h-4 w-4 text-primary" />
            NLP Pipeline Architecture
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row items-start lg:items-center gap-3">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.step} className="flex items-center gap-3 flex-1">
                <div className="flex flex-col items-center gap-1 min-w-0 flex-1">
                  <div className="flex items-center gap-2 w-full">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold font-mono text-primary">
                        {step.step}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-sm font-medium text-foreground truncate">
                        {step.title}
                      </h4>
                      <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div className="hidden lg:block text-muted-foreground/30 text-xl shrink-0">
                    {">"}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
