"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileText, ExternalLink, TrendingUp } from "lucide-react"

interface Citation {
  text: string
  page: number
  confidence: number
  pdfName: string
}

interface CitationModalProps {
  citation: Citation
  onClose: () => void
}

export function CitationModal({ citation, onClose }: CitationModalProps) {
  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Source Citation
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Citation Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                {citation.confidence}% Confidence
              </Badge>
              <span className="text-sm text-muted-foreground">Page {citation.page}</span>
            </div>

            <div className="p-4 bg-muted/50 rounded-lg border-l-4 border-primary">
              <p className="text-sm font-medium mb-2">Extracted Text:</p>
              <p className="text-sm italic">"{citation.text}"</p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Source Document:</p>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{citation.pdfName}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-between">
            <Button variant="outline" className="flex items-center gap-2 bg-transparent">
              <ExternalLink className="h-4 w-4" />
              View Full Document
            </Button>
            <Button onClick={onClose}>Close</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
