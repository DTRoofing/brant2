"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, TrendingUp } from "lucide-react"

interface ExtractedDataItem {
  type: string
  value: string
  confidence: number
}

interface ExtractedDataPreviewProps {
  data: ExtractedDataItem[]
}

export function ExtractedDataPreview({ data }: ExtractedDataPreviewProps) {
  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Extracted Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <div className="animate-pulse">Waiting for AI analysis to begin...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-primary" />
          Extracted Data
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-muted/50 rounded-lg animate-in slide-in-from-left duration-500"
              style={{ animationDelay: `${index * 200}ms` }}
            >
              <div className="flex-1">
                <div className="font-medium text-sm">{item.type}</div>
                <div className="text-muted-foreground text-xs">{item.value}</div>
              </div>

              <div className="flex items-center gap-2">
                <Badge
                  variant="secondary"
                  className={`text-xs ${
                    item.confidence >= 95
                      ? "bg-primary text-primary-foreground" // Fixed high confidence badge contrast
                      : item.confidence >= 90
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-orange-100 text-orange-800"
                  }`}
                >
                  {item.confidence}%
                </Badge>
                <TrendingUp className="h-3 w-3 text-primary" />
              </div>
            </div>
          ))}

          {data.length > 0 && (
            <div className="text-xs text-muted-foreground text-center pt-2">
              More data will appear as analysis continues...
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
