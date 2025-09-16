"use client"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Download, FileText, Table, BarChart3, ChevronDown, Settings } from "lucide-react"

interface QuickExportButtonsProps {
  estimateId: string
  onExport: (type: string, options?: any) => void
  onAdvancedExport?: () => void
}

export function QuickExportButtons({ estimateId, onExport, onAdvancedExport }: QuickExportButtonsProps) {
  const handleQuickExport = async (type: string, options = {}) => {
    try {
      let endpoint = ""
      let payload = { estimateId, ...options }

      switch (type) {
        case "pdf-summary":
          endpoint = "/api/export/pdf"
          payload = { ...payload, format: "summary" }
          break
        case "pdf-detailed":
          endpoint = "/api/export/pdf"
          payload = { ...payload, format: "detailed" }
          break
        case "pdf-quote":
          endpoint = "/api/export/pdf"
          payload = { ...payload, format: "quote" }
          break
        case "excel-basic":
          endpoint = "/api/export/excel"
          payload = { ...payload, includeCharts: false }
          break
        case "excel-detailed":
          endpoint = "/api/export/excel"
          payload = { ...payload, includeCharts: true }
          break
        case "csv-all":
          endpoint = "/api/export/csv"
          payload = { ...payload, sections: ["all"] }
          break
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const result = await response.json()

      if (result.success) {
        // Handle download based on type
        if (type === "csv-all" && result.content) {
          const blob = new Blob([result.content], { type: "text/csv" })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement("a")
          a.href = url
          a.download = result.data.filename
          a.click()
          window.URL.revokeObjectURL(url)
        } else if (result.downloadUrl) {
          window.open(result.downloadUrl, "_blank")
        }

        onExport(type, result)
      }
    } catch (error) {
      console.error("[v0] Quick export failed:", error)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export
          <ChevronDown className="h-4 w-4 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {/* Quick Export Options */}
        <DropdownMenuItem onClick={() => handleQuickExport("pdf-summary")}>
          <FileText className="h-4 w-4 mr-2" />
          PDF Summary Report
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleQuickExport("pdf-detailed")}>
          <FileText className="h-4 w-4 mr-2" />
          PDF Detailed Report
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleQuickExport("pdf-quote")}>
          <FileText className="h-4 w-4 mr-2" />
          PDF Client Quote
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem onClick={() => handleQuickExport("excel-basic")}>
          <Table className="h-4 w-4 mr-2" />
          Excel Basic
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleQuickExport("excel-detailed")}>
          <Table className="h-4 w-4 mr-2" />
          Excel with Charts
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem onClick={() => handleQuickExport("csv-all")}>
          <BarChart3 className="h-4 w-4 mr-2" />
          CSV Data Export
        </DropdownMenuItem>

        {onAdvancedExport && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={onAdvancedExport}>
              <Settings className="h-4 w-4 mr-2" />
              Advanced Export Options...
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
