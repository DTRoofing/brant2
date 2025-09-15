"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Eye, Download, MoreHorizontal, Building, Calendar, DollarSign, AlertTriangle } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ExportDialog } from "@/components/export/export-dialog"
import { formatDate } from "@/lib/date-utils"

export function RecentEstimates() {
  const estimates = [
    {
      id: "EST-2024-001",
      projectName: "Warehouse Complex Roof Replacement",
      client: "ABC Manufacturing",
      date: "2024-01-15",
      status: "completed",
      value: "$127,500",
      sqft: "15,000",
      sqftSource: "pdf_extracted",
    },
    {
      id: "EST-2024-002",
      projectName: "Office Building Repair",
      client: "Tech Solutions Inc",
      date: "2024-01-14",
      status: "in-review",
      value: "$45,200",
      sqft: null, // Added null sqft to demonstrate missing data
      sqftSource: null,
    },
    {
      id: "EST-2024-003",
      projectName: "Retail Center New Installation",
      client: "Shopping Plaza LLC",
      date: "2024-01-12",
      status: "draft",
      value: "$89,750",
      sqft: "12,200",
      sqftSource: "pdf_extracted",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-primary text-primary-foreground"
      case "in-review":
        return "bg-yellow-500 text-yellow-50"
      case "draft":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const displaySquareFootage = (sqft: string | null, sqftSource: string | null) => {
    if (!sqft) {
      return (
        <div className="flex items-center gap-1 text-orange-600">
          <AlertTriangle className="h-3 w-3" />
          <span className="text-xs">Sq ft required</span>
        </div>
      )
    }

    return (
      <div className="flex items-center gap-1">
        <span>{sqft} sq ft</span>
        {sqftSource === "pdf_extracted" && (
          <Badge variant="outline" className="text-xs ml-1">
            PDF
          </Badge>
        )}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recent Estimates</CardTitle>
            <CardDescription>Your latest roofing project estimates and their status</CardDescription>
          </div>
          <Button variant="outline">View All</Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {estimates.map((estimate) => (
            <div
              key={estimate.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-3">
                  <h4 className="font-semibold">{estimate.projectName}</h4>
                  <Badge className={getStatusColor(estimate.status)}>{estimate.status.replace("-", " ")}</Badge>
                </div>

                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Building className="h-3 w-3" />
                    {estimate.client}
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(estimate.date)}
                  </div>
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-3 w-3" />
                    {estimate.value}
                  </div>
                  {displaySquareFootage(estimate.sqft, estimate.sqftSource)}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
                <ExportDialog
                  estimateId={estimate.id}
                  trigger={
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  }
                />
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>Edit Estimate</DropdownMenuItem>
                    <DropdownMenuItem>Duplicate</DropdownMenuItem>
                    <DropdownMenuItem>Share</DropdownMenuItem>
                    <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
