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

export default function DashboardDemoPage() {
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
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-primary/5">
      <DashboardHeader />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome to Brant Roofing System</h1>
          <p className="text-muted-foreground">Upload your roofing plans and get instant AI-powered estimates</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center space-x-1 text-xs">
                  <Badge variant={stat.trend === "up" ? "default" : "secondary"} className="h-5">
                    {stat.change}
                  </Badge>
                  <span className="text-muted-foreground">{stat.description}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Upload Section */}
        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Upload Documents</CardTitle>
              <CardDescription>Drag and drop your roofing plans or click to browse</CardDescription>
            </CardHeader>
            <CardContent>
              <UploadZone />
            </CardContent>
          </Card>
        </div>

        {/* Recent Estimates */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Estimates</CardTitle>
            <CardDescription>Your latest processed documents</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentEstimates />
          </CardContent>
        </Card>
      </main>
    </div>
  )
}