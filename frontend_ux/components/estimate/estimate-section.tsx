"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Package, Users, FileCheck, Wrench, AlertTriangle, ExternalLink, Edit } from "lucide-react"
import { useState } from "react"

const iconMap = {
  Package,
  Users,
  FileCheck,
  Wrench,
  AlertTriangle,
}

interface EstimateItem {
  id: string
  description: string
  quantity: string
  unit: string
  unitCost: number
  totalCost: number
  source: string
  citation: any
}

interface EstimateSection {
  id: string
  title: string
  icon: keyof typeof iconMap
  items: EstimateItem[]
}

interface EstimateSectionProps {
  section: EstimateSection
  onCitationClick: (citation: any) => void
}

export function EstimateSection({ section, onCitationClick }: EstimateSectionProps) {
  const [editingItem, setEditingItem] = useState<string | null>(null)
  const Icon = iconMap[section.icon]

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
  }

  const getSectionTotal = () => {
    return section.items.reduce((total, item) => total + item.totalCost, 0)
  }

  const getSourceBadge = (source: string) => {
    switch (source) {
      case "AI Extracted":
        return <Badge className="bg-primary text-primary-foreground">AI Extracted</Badge>
      case "Manual Input Required":
        return <Badge variant="destructive">Manual Input Required</Badge>
      case "Standard Rate":
        return <Badge variant="secondary">Standard Rate</Badge>
      case "Standard Practice":
        return <Badge variant="outline">Standard Practice</Badge>
      default:
        return <Badge variant="outline">{source}</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5" />
            {section.title}
          </CardTitle>
          <div className="text-right">
            <div className="text-2xl font-bold">{formatCurrency(getSectionTotal())}</div>
            <div className="text-sm text-muted-foreground">Section Total</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-muted-foreground border-b pb-2">
            <div className="col-span-4">Description</div>
            <div className="col-span-2">Quantity</div>
            <div className="col-span-2">Unit Cost</div>
            <div className="col-span-2">Total</div>
            <div className="col-span-2">Source</div>
          </div>

          {/* Table Rows */}
          {section.items.map((item) => (
            <div key={item.id} className="grid grid-cols-12 gap-4 items-center py-2 border-b border-muted/50">
              <div className="col-span-4">
                <div className="font-medium">{item.description}</div>
                {item.citation && (
                  <Button
                    variant="link"
                    size="sm"
                    className="h-auto p-0 text-xs text-primary"
                    onClick={() => onCitationClick(item.citation)}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    View Source
                  </Button>
                )}
              </div>

              <div className="col-span-2">
                {editingItem === item.id ? (
                  <Input defaultValue={item.quantity} className="h-8" />
                ) : (
                  <span>
                    {item.quantity} {item.unit}
                  </span>
                )}
              </div>

              <div className="col-span-2">
                {editingItem === item.id ? (
                  <Input defaultValue={item.unitCost.toString()} className="h-8" />
                ) : (
                  <span>{formatCurrency(item.unitCost)}</span>
                )}
              </div>

              <div className="col-span-2">
                <span className="font-medium">{formatCurrency(item.totalCost)}</span>
              </div>

              <div className="col-span-2 flex items-center justify-between">
                {getSourceBadge(item.source)}
                {item.source === "Manual Input Required" && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditingItem(editingItem === item.id ? null : item.id)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
