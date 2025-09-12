"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Building2, Share, Edit, FileText, Calculator, Save, X, ArrowLeft, Brain } from "lucide-react"
import { EstimateSummary } from "@/components/estimate/estimate-summary"
import { EstimateSection } from "@/components/estimate/estimate-section"
import { CitationModal } from "@/components/estimate/citation-modal"
import { QuickExportButtons } from "@/components/export/quick-export-buttons"

export default function EstimatePage() {
  const [selectedCitation, setSelectedCitation] = useState<any>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isNewEstimate, setIsNewEstimate] = useState(false)
  const [estimateData, setEstimateData] = useState<any>(null)

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const estimateId = urlParams.get("id")

    if (!estimateId || estimateId === "new") {
      setIsNewEstimate(true)
      setEstimateData(getDefaultEstimateData())
    } else {
      setEstimateData(getMockEstimateData())
    }
  }, [])

  const getDefaultEstimateData = () => ({
    projectInfo: {
      name: "New Roofing Estimate",
      client: "Enter Client Name",
      address: "Enter Project Address",
      sqft: null,
      sqftSource: null,
      roofType: "To be determined",
      date: new Date().toISOString().split("T")[0],
      estimateId: `EST-${Date.now()}`,
    },
    summary: {
      totalCost: 0,
      laborCost: 0,
      materialCost: 0,
      permitCost: 0,
      contingency: 0,
      timeline: "To be determined",
      confidence: 0,
    },
    sections: [],
    claudeAnalysis: {
      summary: {
        projectType: "Pending Analysis",
        totalSquareFootage: 0,
        roofType: "To be determined",
        estimatedTotal: 0,
        confidence: 0,
        analysisDate: new Date().toISOString(),
      },
      expertRecommendations: [],
      detailedAnalysis: {
        structuralAssessment: "Awaiting PDF analysis...",
        drainageEvaluation: "Awaiting PDF analysis...",
        accessConsiderations: "Awaiting PDF analysis...",
        permitRequirements: "Awaiting PDF analysis...",
      },
      lineItems: [],
    },
  })

  const getMockEstimateData = () => ({
    projectInfo: {
      name: "Warehouse Complex Roof Replacement",
      client: "ABC Manufacturing",
      address: "1234 Industrial Blvd, Manufacturing District",
      sqft: "15,000",
      sqftSource: "pdf_extracted",
      roofType: "Commercial TPO Membrane",
      date: "2024-01-15",
      estimateId: "EST-2024-001",
    },
    summary: {
      totalCost: 127500,
      laborCost: 45000,
      materialCost: 65000,
      permitCost: 2500,
      contingency: 15000,
      timeline: "3-4 weeks",
      confidence: 94,
    },
    sections: [
      {
        id: "materials",
        title: "Materials",
        icon: "Package",
        items: [
          {
            id: "tpo-membrane",
            description: "TPO Membrane 60 mil",
            quantity: "16,500",
            unit: "sq ft",
            unitCost: 2.85,
            totalCost: 47025,
            source: "AI Extracted",
            citation: {
              text: "TPO membrane roofing system, 60 mil thickness",
              page: 3,
              confidence: 96,
              pdfName: "warehouse-roof-specs.pdf",
            },
          },
          {
            id: "insulation",
            description: "Polyiso Insulation R-30",
            quantity: "15,000",
            unit: "sq ft",
            unitCost: 1.2,
            totalCost: 18000,
            source: "AI Extracted",
            citation: {
              text: "R-30 polyisocyanurate insulation board",
              page: 4,
              confidence: 92,
              pdfName: "warehouse-roof-specs.pdf",
            },
          },
          {
            id: "fasteners",
            description: "Roofing Fasteners & Plates",
            quantity: "2,400",
            unit: "pieces",
            unitCost: 0.75,
            totalCost: 1800,
            source: "Manual Input Required",
            citation: null,
          },
        ],
      },
      {
        id: "labor",
        title: "Labor",
        icon: "Users",
        items: [
          {
            id: "tear-off",
            description: "Existing Roof Tear-off",
            quantity: "15,000",
            unit: "sq ft",
            unitCost: 1.5,
            totalCost: 22500,
            source: "AI Extracted",
            citation: {
              text: "Remove existing built-up roofing system",
              page: 2,
              confidence: 89,
              pdfName: "warehouse-roof-specs.pdf",
            },
          },
          {
            id: "installation",
            description: "TPO Installation",
            quantity: "15,000",
            unit: "sq ft",
            unitCost: 1.5,
            totalCost: 22500,
            source: "Standard Rate",
            citation: null,
          },
          {
            id: "cleanup",
            description: "Site Cleanup & Disposal",
            quantity: "1",
            unit: "job",
            unitCost: 3500,
            totalCost: 3500,
            source: "Manual Input Required",
            citation: null,
          },
        ],
      },
      {
        id: "permits",
        title: "Permits & Fees",
        icon: "FileCheck",
        items: [
          {
            id: "building-permit",
            description: "Building Permit",
            quantity: "1",
            unit: "permit",
            unitCost: 1500,
            totalCost: 1500,
            source: "Manual Input Required",
            citation: null,
          },
          {
            id: "inspection-fees",
            description: "Inspection Fees",
            quantity: "3",
            unit: "inspections",
            unitCost: 250,
            totalCost: 750,
            source: "Manual Input Required",
            citation: null,
          },
        ],
      },
      {
        id: "equipment",
        title: "Equipment & Tools",
        icon: "Wrench",
        items: [
          {
            id: "crane-rental",
            description: "Crane Rental",
            quantity: "5",
            unit: "days",
            unitCost: 800,
            totalCost: 4000,
            source: "Manual Input Required",
            citation: null,
          },
          {
            id: "safety-equipment",
            description: "Safety Equipment & Barriers",
            quantity: "1",
            unit: "job",
            unitCost: 1200,
            totalCost: 1200,
            source: "Manual Input Required",
            citation: null,
          },
        ],
      },
      {
        id: "contingency",
        title: "Contingency & Risk",
        icon: "AlertTriangle",
        items: [
          {
            id: "weather-delays",
            description: "Weather Delay Contingency",
            quantity: "1",
            unit: "allowance",
            unitCost: 5000,
            totalCost: 5000,
            source: "Standard Practice",
            citation: null,
          },
          {
            id: "structural-issues",
            description: "Structural Repair Allowance",
            quantity: "1",
            unit: "allowance",
            unitCost: 10000,
            totalCost: 10000,
            source: "Manual Input Required",
            citation: null,
          },
        ],
      },
    ],
    claudeAnalysis: {
      summary: {
        projectType: "Commercial Roof Replacement",
        totalSquareFootage: 15000,
        roofType: "TPO Membrane System",
        estimatedTotal: 142750,
        confidence: 0.87,
        analysisDate: "2024-01-15T10:30:00Z",
      },
      expertRecommendations: [
        {
          category: "Materials",
          recommendation: "Upgrade to 80-mil TPO membrane for enhanced durability in industrial environment",
          impact: "Additional $8,250 cost but 25% longer lifespan",
          confidence: 0.92,
        },
        {
          category: "Labor",
          recommendation: "Schedule installation during dry season (May-September) to minimize weather delays",
          impact: "Reduces contingency needs by 30%",
          confidence: 0.89,
        },
        {
          category: "Safety",
          recommendation: "Install temporary roof anchors for fall protection during multi-day installation",
          impact: "Additional $2,400 but ensures OSHA compliance",
          confidence: 0.95,
        },
      ],
      detailedAnalysis: {
        structuralAssessment:
          "Existing roof deck appears adequate based on specifications. Recommend structural engineer verification for areas with visible deflection.",
        drainageEvaluation:
          "Current drainage system adequate but recommend adding two additional roof drains in low-slope areas identified in plans.",
        accessConsiderations:
          "Crane access limited to north side of building. Factor additional material handling time.",
        permitRequirements:
          "Commercial permit required. Expect 2-3 week approval process. Fire department inspection needed for buildings over 10,000 sq ft.",
      },
      lineItems: [
        {
          category: "MATERIAL",
          description: "TPO Membrane 80-mil (Upgraded)",
          quantity: 16500,
          unit: "sq ft",
          unitCost: 3.35,
          totalCost: 55275,
          confidence: 0.94,
          sourceReference: "Page 3 - Membrane specifications",
        },
        {
          category: "LABOR",
          description: "Membrane Installation with Mechanical Attachment",
          quantity: 15000,
          unit: "sq ft",
          unitCost: 2.25,
          totalCost: 33750,
          confidence: 0.88,
          sourceReference: "Page 5 - Installation requirements",
        },
        {
          category: "SAFETY",
          description: "Temporary Roof Anchor System",
          quantity: 12,
          unit: "anchors",
          unitCost: 200,
          totalCost: 2400,
          confidence: 0.95,
          sourceReference: "Safety requirements inferred from building height",
        },
      ],
    },
  })

  const handleExport = (type: string, result: any) => {
    console.log("[v0] Export completed:", type, result)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const response = await fetch(`/api/estimates/${estimateData.projectInfo.estimateId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(estimateData),
      })

      if (response.ok) {
        setHasUnsavedChanges(false)
        console.log("[v0] Estimate saved successfully")
      }
    } catch (error) {
      console.error("[v0] Error saving estimate:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleSaveAndClose = async () => {
    await handleSave()
    window.location.href = "/dashboard"
  }

  const handleDiscard = () => {
    setHasUnsavedChanges(false)
    window.location.href = "/dashboard"
  }

  if (!estimateData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading estimate...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="sticky top-0 z-50 bg-white border-b-2 border-primary/20 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="default" size="sm" onClick={handleSave} disabled={isSaving || !hasUnsavedChanges}>
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? "Saving..." : "Save"}
              </Button>
              <Button variant="outline" size="sm" onClick={handleSaveAndClose} disabled={isSaving}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Save & Close
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDiscard}
                disabled={isSaving}
                className="text-red-600 border-red-600 hover:bg-red-50 bg-transparent"
              >
                <X className="h-4 w-4 mr-2" />
                Discard
              </Button>
              {hasUnsavedChanges && (
                <Badge variant="outline" className="text-orange-600 border-orange-600 ml-2 animate-pulse">
                  ● Unsaved Changes
                </Badge>
              )}
              {isNewEstimate && (
                <Badge variant="outline" className="text-blue-600 border-blue-600 ml-2">
                  ● New Estimate
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant="outline" size="sm">
                <Share className="h-4 w-4 mr-2" />
                Share
              </Button>
              <QuickExportButtons estimateId={estimateData.projectInfo.estimateId} onExport={handleExport} />
            </div>
          </div>
        </div>
      </div>

      <div className="border-b bg-gradient-to-r from-primary/5 to-blue-50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary rounded-xl shadow-sm">
              <Building2 className="h-7 w-7 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-2xl text-slate-900">Roofing Estimate</h1>
              <p className="text-base text-slate-600">{estimateData.projectInfo.name}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <EstimateSummary projectInfo={estimateData.projectInfo} summary={estimateData.summary} />

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Detailed Estimate Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="all" className="space-y-6">
                <TabsList className="grid w-full grid-cols-7 h-12">
                  <TabsTrigger value="all" className="text-sm">
                    All Items
                  </TabsTrigger>
                  <TabsTrigger value="materials" className="text-sm">
                    Materials
                  </TabsTrigger>
                  <TabsTrigger value="labor" className="text-sm">
                    Labor
                  </TabsTrigger>
                  <TabsTrigger value="permits" className="text-sm">
                    Permits
                  </TabsTrigger>
                  <TabsTrigger value="equipment" className="text-sm">
                    Equipment
                  </TabsTrigger>
                  <TabsTrigger value="contingency" className="text-sm">
                    Contingency
                  </TabsTrigger>
                  <TabsTrigger
                    value="claude-expert"
                    className="text-sm bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 border-2 border-purple-300 data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600 data-[state=active]:text-white font-semibold"
                  >
                    <Brain className="h-4 w-4 mr-1" />
                    Claude AI
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="space-y-6">
                  {estimateData.sections.map((section) => (
                    <EstimateSection key={section.id} section={section} onCitationClick={setSelectedCitation} />
                  ))}
                </TabsContent>

                {estimateData.sections.map((section) => (
                  <TabsContent key={section.id} value={section.id}>
                    <EstimateSection section={section} onCitationClick={setSelectedCitation} />
                  </TabsContent>
                ))}

                <TabsContent value="claude-expert" className="space-y-6">
                  <div className="grid gap-6">
                    <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-purple-900">
                          <Brain className="h-5 w-5 text-purple-600" />
                          Claude AI Expert Analysis Summary
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center p-3 bg-white rounded-lg border">
                            <div className="text-2xl font-bold text-purple-600">
                              ${estimateData.claudeAnalysis.summary.estimatedTotal.toLocaleString()}
                            </div>
                            <div className="text-sm text-muted-foreground">Expert Total</div>
                          </div>
                          <div className="text-center p-3 bg-white rounded-lg border">
                            <div className="text-2xl font-bold text-blue-600">
                              {Math.round(estimateData.claudeAnalysis.summary.confidence * 100)}%
                            </div>
                            <div className="text-sm text-muted-foreground">Confidence</div>
                          </div>
                          <div className="text-center p-3 bg-white rounded-lg border">
                            <div className="text-2xl font-bold text-emerald-600">
                              {estimateData.claudeAnalysis.summary.totalSquareFootage.toLocaleString()}
                            </div>
                            <div className="text-sm text-muted-foreground">Sq Ft</div>
                          </div>
                          <div className="text-center p-3 bg-white rounded-lg border">
                            <div className="text-2xl font-bold text-orange-600">
                              {estimateData.claudeAnalysis.expertRecommendations.length}
                            </div>
                            <div className="text-sm text-muted-foreground">Recommendations</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-slate-900">Expert Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {estimateData.claudeAnalysis.expertRecommendations.map((rec, index) => (
                          <div key={index} className="p-4 border rounded-lg bg-slate-50">
                            <div className="flex items-start justify-between mb-2">
                              <Badge variant="outline" className="text-purple-600 border-purple-600">
                                {rec.category}
                              </Badge>
                              <Badge variant="secondary" className="bg-primary text-primary-foreground">
                                {Math.round(rec.confidence * 100)}% Confidence
                              </Badge>
                            </div>
                            <h4 className="font-semibold text-slate-900 mb-1">{rec.recommendation}</h4>
                            <p className="text-sm text-slate-600">{rec.impact}</p>
                          </div>
                        ))}
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-slate-900">Detailed Professional Analysis</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid gap-4">
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2">Structural Assessment</h4>
                            <p className="text-sm text-slate-600">
                              {estimateData.claudeAnalysis.detailedAnalysis.structuralAssessment}
                            </p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2">Drainage Evaluation</h4>
                            <p className="text-sm text-slate-600">
                              {estimateData.claudeAnalysis.detailedAnalysis.drainageEvaluation}
                            </p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2">Access Considerations</h4>
                            <p className="text-sm text-slate-600">
                              {estimateData.claudeAnalysis.detailedAnalysis.accessConsiderations}
                            </p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2">Permit Requirements</h4>
                            <p className="text-sm text-slate-600">
                              {estimateData.claudeAnalysis.detailedAnalysis.permitRequirements}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-slate-900">Claude Expert Line Items</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {estimateData.claudeAnalysis.lineItems.map((item, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-4 border rounded-lg bg-gradient-to-r from-purple-50 to-blue-50"
                            >
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge variant="outline" className="text-xs">
                                    {item.category}
                                  </Badge>
                                  <Badge variant="secondary" className="bg-primary text-primary-foreground text-xs">
                                    {Math.round(item.confidence * 100)}% Confidence
                                  </Badge>
                                </div>
                                <h4 className="font-medium text-slate-900">{item.description}</h4>
                                <p className="text-sm text-slate-600">{item.sourceReference}</p>
                              </div>
                              <div className="text-right">
                                <div className="font-semibold text-slate-900">${item.totalCost.toLocaleString()}</div>
                                <div className="text-sm text-slate-600">
                                  {item.quantity.toLocaleString()} {item.unit} × ${item.unitCost}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-900">
                <FileText className="h-5 w-5 text-primary" />
                AI Analysis Notes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm text-slate-900">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-900">
                    <strong className="text-slate-900 font-semibold">High Confidence Items:</strong> Materials and basic
                    labor costs were extracted with 90%+ confidence from the provided specifications.
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-900">
                    <strong className="text-slate-900 font-semibold">Manual Review Required:</strong> Permit costs,
                    equipment rental, and contingency items require local market knowledge and manual input.
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-900">
                    <strong className="text-slate-900 font-semibold">Square Footage:</strong> Building area was
                    successfully extracted from PDF with high confidence. All area-based calculations use only
                    PDF-sourced measurements.
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-900">
                    <strong className="text-slate-900 font-semibold">Recommendations:</strong> Consider weather
                    protection during installation and verify local permit requirements before finalizing estimate.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {selectedCitation && <CitationModal citation={selectedCitation} onClose={() => setSelectedCitation(null)} />}
    </div>
  )
}
