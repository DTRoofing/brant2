"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Building, MapPin, Calendar, Ruler, DollarSign, Clock, TrendingUp } from "lucide-react"
import { formatDate } from "@/lib/date-utils"

interface ProjectInfo {
  name: string
  client: string
  address: string
  sqft: string | null // Allow null for missing data
  sqftSource?: string // Track data source
  roofType: string
  date: string
  estimateId: string
}

interface Summary {
  totalCost: number
  laborCost: number
  materialCost: number
  permitCost: number
  contingency: number
  timeline: string
  confidence: number
}

interface EstimateSummaryProps {
  projectInfo: ProjectInfo
  summary: Summary
}

export function EstimateSummary({ projectInfo, summary }: EstimateSummaryProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
  }

  const displaySquareFootage = () => {
    if (!projectInfo.sqft || projectInfo.sqft === "0") {
      return (
        <div className="flex items-center gap-2">
          <Ruler className="h-4 w-4 text-orange-500" />
          <span className="text-orange-600 font-medium">More data required</span>
          <Badge variant="outline" className="text-xs text-orange-600 border-orange-200">
            Not found in PDF
          </Badge>
        </div>
      )
    }

    return (
      <div className="flex items-center gap-2">
        <Ruler className="h-4 w-4 text-muted-foreground" />
        <span>{projectInfo.sqft} sq ft</span>
        {projectInfo.sqftSource && (
          <Badge variant="outline" className="text-xs">
            PDF extracted
          </Badge>
        )}
      </div>
    )
  }

  const calculateCostPerSqFt = () => {
    if (!projectInfo.sqft || projectInfo.sqft === "0") {
      return "Requires sq ft data"
    }
    const sqftNumber = Number.parseInt(projectInfo.sqft.replace(",", ""))
    return formatCurrency(summary.totalCost / sqftNumber)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Project Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building className="h-5 w-5" />
            Project Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg text-balance">{projectInfo.name}</h3>
            <p className="text-muted-foreground">{projectInfo.client}</p>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span>{projectInfo.address}</span>
            </div>
            {displaySquareFootage()}
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>{formatDate(projectInfo.date)}</span>
            </div>
          </div>

          <div className="pt-2">
            <Badge variant="outline">{projectInfo.roofType}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Cost Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{formatCurrency(summary.totalCost)}</div>
            <p className="text-sm text-muted-foreground">Total Project Cost</p>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Materials</span>
              <span className="font-medium">{formatCurrency(summary.materialCost)}</span>
            </div>
            <div className="flex justify-between">
              <span>Labor</span>
              <span className="font-medium">{formatCurrency(summary.laborCost)}</span>
            </div>
            <div className="flex justify-between">
              <span>Permits & Fees</span>
              <span className="font-medium">{formatCurrency(summary.permitCost)}</span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span>Contingency</span>
              <span className="font-medium">{formatCurrency(summary.contingency)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Project Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Project Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Timeline</span>
                <span className="font-medium">{summary.timeline}</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">AI Confidence</span>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  <span className="font-medium">{summary.confidence}%</span>
                </div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Cost per Sq Ft</span>
                <span className="font-medium text-sm">{calculateCostPerSqFt()}</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Estimate ID</span>
                <span className="font-mono text-sm">{projectInfo.estimateId}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
