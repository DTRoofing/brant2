"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Download, FileText, Table, BarChart3, Loader2, CheckCircle } from "lucide-react"

interface ExportDialogProps {
  estimateId: string
  trigger?: React.ReactNode
}

export function ExportDialog({ estimateId, trigger }: ExportDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [exportType, setExportType] = useState("pdf")
  const [pdfFormat, setPdfFormat] = useState("detailed")
  const [excelOptions, setExcelOptions] = useState({
    includeCharts: true,
    includeSummary: true,
    includeLineItems: true,
  })
  const [csvSections, setCsvSections] = useState(["all"])
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportComplete, setExportComplete] = useState(false)
  const [downloadUrl, setDownloadUrl] = useState("")

  const handleExport = async () => {
    setIsExporting(true)
    setExportProgress(0)

    try {
      let endpoint = ""
      let payload = { estimateId }

      switch (exportType) {
        case "pdf":
          endpoint = "/api/export/pdf"
          payload = { ...payload, format: pdfFormat }
          break
        case "excel":
          endpoint = "/api/export/excel"
          payload = { ...payload, ...excelOptions }
          break
        case "csv":
          endpoint = "/api/export/csv"
          payload = { ...payload, sections: csvSections }
          break
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setExportProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const result = await response.json()

      if (result.success) {
        setExportProgress(100)
        setExportComplete(true)
        setDownloadUrl(result.downloadUrl)

        // Auto-download for CSV
        if (exportType === "csv" && result.content) {
          const blob = new Blob([result.content], { type: "text/csv" })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement("a")
          a.href = url
          a.download = result.data.filename
          a.click()
          window.URL.revokeObjectURL(url)
        }
      }
    } catch (error) {
      console.error("[v0] Export failed:", error)
    } finally {
      setIsExporting(false)
    }
  }

  const resetDialog = () => {
    setExportProgress(0)
    setExportComplete(false)
    setDownloadUrl("")
    setIsExporting(false)
  }

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open)
        if (!open) resetDialog()
      }}
    >
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Export Estimate</DialogTitle>
        </DialogHeader>

        {!isExporting && !exportComplete && (
          <div className="space-y-6">
            {/* Export Format Selection */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Choose Export Format</h3>
              <RadioGroup value={exportType} onValueChange={setExportType} className="grid grid-cols-3 gap-4">
                <div>
                  <RadioGroupItem value="pdf" id="pdf" className="peer sr-only" />
                  <Label
                    htmlFor="pdf"
                    className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                  >
                    <FileText className="mb-3 h-6 w-6" />
                    <div className="text-center">
                      <div className="font-medium">PDF Report</div>
                      <div className="text-xs text-muted-foreground">Professional estimate document</div>
                    </div>
                  </Label>
                </div>

                <div>
                  <RadioGroupItem value="excel" id="excel" className="peer sr-only" />
                  <Label
                    htmlFor="excel"
                    className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                  >
                    <Table className="mb-3 h-6 w-6" />
                    <div className="text-center">
                      <div className="font-medium">Excel Workbook</div>
                      <div className="text-xs text-muted-foreground">Spreadsheet with calculations</div>
                    </div>
                  </Label>
                </div>

                <div>
                  <RadioGroupItem value="csv" id="csv" className="peer sr-only" />
                  <Label
                    htmlFor="csv"
                    className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                  >
                    <BarChart3 className="mb-3 h-6 w-6" />
                    <div className="text-center">
                      <div className="font-medium">CSV Data</div>
                      <div className="text-xs text-muted-foreground">Raw data for analysis</div>
                    </div>
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {/* Format-specific Options */}
            {exportType === "pdf" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">PDF Options</CardTitle>
                </CardHeader>
                <CardContent>
                  <RadioGroup value={pdfFormat} onValueChange={setPdfFormat} className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="detailed" id="detailed" />
                      <Label htmlFor="detailed">Detailed Report (8 pages)</Label>
                      <Badge variant="secondary">Recommended</Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="summary" id="summary" />
                      <Label htmlFor="summary">Summary Report (3 pages)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="quote" id="quote" />
                      <Label htmlFor="quote">Client Quote (1 page)</Label>
                    </div>
                  </RadioGroup>
                </CardContent>
              </Card>
            )}

            {exportType === "excel" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Excel Options</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="charts"
                      checked={excelOptions.includeCharts}
                      onCheckedChange={(checked) => setExcelOptions((prev) => ({ ...prev, includeCharts: !!checked }))}
                    />
                    <Label htmlFor="charts">Include Charts & Graphs</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="summary"
                      checked={excelOptions.includeSummary}
                      onCheckedChange={(checked) => setExcelOptions((prev) => ({ ...prev, includeSummary: !!checked }))}
                    />
                    <Label htmlFor="summary">Summary Worksheet</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="lineitems"
                      checked={excelOptions.includeLineItems}
                      onCheckedChange={(checked) =>
                        setExcelOptions((prev) => ({ ...prev, includeLineItems: !!checked }))
                      }
                    />
                    <Label htmlFor="lineitems">Detailed Line Items</Label>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setIsOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Generate Export
              </Button>
            </div>
          </div>
        )}

        {/* Export Progress */}
        {isExporting && (
          <div className="space-y-6 text-center">
            <div className="space-y-2">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <h3 className="text-lg font-semibold">Generating Export</h3>
              <p className="text-muted-foreground">Creating your {exportType.toUpperCase()} export, please wait...</p>
            </div>

            <div className="space-y-2">
              <Progress value={exportProgress} className="h-2" />
              <p className="text-sm text-muted-foreground">{exportProgress}% complete</p>
            </div>
          </div>
        )}

        {/* Export Complete */}
        {exportComplete && (
          <div className="space-y-6 text-center">
            <div className="space-y-2">
              <CheckCircle className="h-8 w-8 mx-auto text-primary" />
              <h3 className="text-lg font-semibold">Export Complete</h3>
              <p className="text-muted-foreground">
                Your {exportType.toUpperCase()} file has been generated successfully.
              </p>
            </div>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={() => setIsOpen(false)}>
                Close
              </Button>
              {downloadUrl && (
                <Button asChild>
                  <a href={downloadUrl} download>
                    <Download className="h-4 w-4 mr-2" />
                    Download File
                  </a>
                </Button>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
