"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Upload, FileText, TrendingUp, Clock, DollarSign, Bot, Download, Plus } from "lucide-react"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { UploadZone } from "@/components/dashboard/upload-zone"
import { RecentEstimates } from "@/components/dashboard/recent-estimates"

export default function DashboardPage() {
  const [dragActive, setDragActive] = useState(false)

  // Mock data for demonstration
  const stats = [
    {
      title: "Total Estimates",
      value: "247",
      change: "+12%",
      trend: "up",
      icon: FileText,
      description: "This month",
    },
    {
      title: "AI Processing",
      value: "98.5%",
      change: "+2.1%",
      trend: "up",
      icon: Bot,
      description: "Accuracy rate",
    },
    {
      title: "Avg. Estimate Value",
      value: "$45,200",
      change: "+8.2%",
      trend: "up",
      icon: DollarSign,
      description: "Per project",
    },
    {
      title: "Processing Time",
      value: "2.3 min",
      change: "-15%",
      trend: "down",
      icon: Clock,
      description: "Average",
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Welcome Section */}
        <div className="flex flex-col gap-4">
          <div>
            <h1 className="text-3xl font-bold text-balance">Welcome back, John</h1>
            <p className="text-muted-foreground text-pretty">
              Upload roofing documents to generate AI-powered estimates instantly
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card key={index} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span
                    className={`flex items-center gap-1 ${stat.trend === "up" ? "text-primary" : "text-destructive"}`}
                  >
                    <TrendingUp className={`h-3 w-3 ${stat.trend === "down" ? "rotate-180" : ""}`} />
                    {stat.change}
                  </span>
                  <span>{stat.description}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Roofing Documents
                </CardTitle>
                <CardDescription>
                  Upload PDFs, blueprints, or specifications to generate comprehensive estimates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <UploadZone />

                {/* AI Features Highlight */}
                <div className="mt-6 p-4 bg-primary/5 rounded-lg border border-primary/20">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-primary/10 rounded-full">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm">AI-Powered Analysis</h4>
                      <p className="text-sm text-muted-foreground mt-1">
                        Our advanced AI extracts measurements, materials, and specifications automatically from your
                        documents with 98.5% accuracy.
                      </p>
                      <div className="flex gap-2 mt-3">
                        <Badge variant="secondary" className="text-xs">
                          Google Document AI
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          Cloud Vision
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          Auto-Extraction
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  New Manual Estimate
                </Button>
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <FileText className="h-4 w-4 mr-2" />
                  View All Estimates
                </Button>
                <Button className="w-full justify-start bg-transparent" variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export Reports
                </Button>
              </CardContent>
            </Card>

            {/* Processing Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Current Processing</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>warehouse-roof-specs.pdf</span>
                      <span className="text-muted-foreground">85%</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>office-building-plans.pdf</span>
                      <span className="text-muted-foreground">45%</span>
                    </div>
                    <Progress value={45} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Recent Estimates */}
        <RecentEstimates />
      </main>
    </div>
  )
}
