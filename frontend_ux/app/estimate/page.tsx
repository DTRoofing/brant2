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
  const [error, setError] = useState<string | null>(null)
  const [dataSource, setDataSource] = useState<string | null>(null)
  const [estimateData, setEstimateData] = useState<any>(null)

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    // Consolidate ID fetching to be more robust. Prioritize 'document_id', then 'documentId', then 'id'.
    const documentId = urlParams.get("document_id") || urlParams.get("documentId") || urlParams.get("id")
    const source = urlParams.get("source")
    setDataSource(source)

    if (documentId && documentId !== "new") {
      // If we have a valid document ID, load its results.
      loadPipelineResults(documentId, source)
    } else {
      // Otherwise, treat it as a new estimate. This handles cases where no ID is present,
      // or the ID is explicitly 'new'.
      setIsNewEstimate(true)
      setEstimateData(getDefaultEstimateData())
    }
  }, [])

  const loadPipelineResults = async (documentId: string, source: string | null) => {
    setError(null)
    try {
      // Always fetch fresh results from the API to ensure data is not stale
      const { apiClient } = await import('@/lib/api')
      localStorage.removeItem('latestEstimateResults') // Clean up any old stored results
      const results = await apiClient.getPipelineResults(documentId)
      setEstimateData(convertPipelineResultsToEstimateData(results, source))
    } catch (error) {
      console.error('Error loading pipeline results:', error)
      let errorMessage = "Failed to load pipeline results. The document may still be processing or an error occurred."
      if (error instanceof Error) {
        errorMessage += ` Details: ${error.message}`
      }
      setError(errorMessage)
      // Do not fall back to default data, show an error state instead.
      setEstimateData(null)
    }
  }

  const calculateTimeline = (sqft: number, complexity: string = 'medium'): string => {
    // Calculate timeline based on square footage and complexity
    if (sqft === 0) return "To be determined"
    
    const baseWeeks = Math.ceil(sqft / 5000) // Base: 1 week per 5000 sqft
    const complexityMultiplier = {
      'low': 0.8,
      'medium': 1.0,
      'high': 1.5,
      'very_high': 2.0
    }[complexity] || 1.0
    
    const weeks = Math.ceil(baseWeeks * complexityMultiplier)
    
    if (weeks === 1) return "1 week"
    if (weeks <= 2) return "1-2 weeks"
    if (weeks <= 4) return "3-4 weeks"
    if (weeks <= 8) return "6-8 weeks"
    return `${weeks-1}-${weeks+1} weeks`
  }

  const formatClientInfo = (metadata: any): { projectName: string; clientName: string; address: string } => {
    // Format client information based on backend metadata
    // This should eventually be done entirely in the backend
    const projectName = metadata.project_name || "Roofing Estimate"
    const clientName = metadata.client_name || metadata.company_name || "Client Name"
    const address = metadata.full_address || metadata.address || "Project Address"
    
    return { projectName, clientName, address }
  }

  const convertPipelineResultsToEstimateData = (results: any, source: string | null) => {
    const roofArea = results.results?.roof_area_sqft || 0
    const totalCost = results.results?.estimated_cost || 0
    const confidence = results.results?.confidence || 0.8
    const metadata = results.results?.metadata || {}
    
    // Determine source and project type more dynamically
    const extractionMethod = results.results?.extraction_method || source || "pipeline"
    const projectType = source === 'claude-direct' 
        ? "Direct Claude Analysis" 
        : "Hybrid Pipeline Analysis"

    // Use backend-formatted client information
    const { projectName, clientName, address } = formatClientInfo(metadata)

    return {
      projectInfo: {
        name: projectName,
        client: clientName,
        address: address,
        sqft: roofArea > 0 ? roofArea.toLocaleString() : "N/A",
        sqftSource: roofArea > 0 ? extractionMethod : null,
        roofType: results.results?.roof_type || results.results?.materials?.[0]?.type || results.results?.materials?.[0] || "To be determined",
        date: new Date().toISOString().split("T")[0],
        estimateId: metadata.project_number || metadata.document_id || `EST-${Date.now()}`,
        metadata: metadata,  // Store full metadata for reference
      },
      summary: {
        totalCost: totalCost,
        // Use cost breakdown from backend if available, otherwise use industry standards
        laborCost: results.results?.labor_cost || (totalCost * 0.4),
        materialCost: results.results?.material_cost || (totalCost * 0.5),
        permitCost: results.results?.permit_cost || (totalCost * 0.05),
        contingency: results.results?.contingency || (totalCost * 0.05),
        timeline: calculateTimeline(roofArea, results.results?.complexity),
        confidence: Math.round(confidence * 100),
      },
      sections: generateSectionsFromPipelineResults(results),
      claudeAnalysis: {
        summary: {
          projectType: projectType,
          totalSquareFootage: roofArea,
          roofType: results.results?.materials?.[0] || "To be determined",
          estimatedTotal: totalCost,
          confidence: confidence,
          analysisDate: new Date().toISOString(),
        },
        expertRecommendations: generateRecommendationsFromResults(results),
        detailedAnalysis: {
          structuralAssessment: "Analysis based on hybrid pipeline processing",
          drainageEvaluation: "Evaluation from blueprint analysis",
          accessConsiderations: "Considerations from roof feature detection",
          permitRequirements: "Standard commercial permit requirements",
        },
        lineItems: generateLineItemsFromResults(results),
      },
    }
  }

  const generateSectionsFromPipelineResults = (results: any) => {
    const sections = []
    const roofArea = results.results?.roof_area_sqft || 0
    const materials = results.results?.materials || []
    const roofFeatures = results.results?.roof_features || []

    // Materials section
    if (materials.length > 0) {
      sections.push({
        id: "materials",
        title: "Materials",
        icon: "Package",
        items: materials.map((material: any, index: number) => ({
          id: `material-${index}`,
          description: material.type || material,
          quantity: roofArea > 0 ? roofArea.toLocaleString() : "TBD",
          unit: "sq ft",
          unitCost: 0,
          totalCost: 0,
          source: "Pipeline Generated",
          citation: null,
        }))
      })
    }

    // Roof features section
    if (roofFeatures.length > 0) {
      sections.push({
        id: "roof_features",
        title: "Roof Features",
        icon: "Wrench",
        items: roofFeatures.map((feature: any, index: number) => ({
          id: `feature-${index}`,
          description: `${feature.type} (${feature.count || 1})`,
          quantity: feature.count || 1,
          unit: "units",
          unitCost: 0,
          totalCost: 0,
          source: "Pipeline Detected",
          citation: null,
        }))
      })
    }

    return sections
  }

  const generateRecommendationsFromResults = (results: any) => {
    const recommendations = []
    const roofFeatures = results.results?.roof_features || []

    if (roofFeatures.some((f: any) => f.type === 'exhaust_port')) {
      recommendations.push({
        category: "Installation",
        recommendation: "Special attention required for exhaust port sealing and flashing",
        impact: "May require additional labor and materials",
        confidence: 0.9,
      })
    }

    if (roofFeatures.some((f: any) => f.type === 'walkway')) {
      recommendations.push({
        category: "Access",
        recommendation: "Existing walkways may affect material delivery and installation",
        impact: "Consider access routes during planning",
        confidence: 0.8,
      })
    }

    return recommendations
  }

  const generateLineItemsFromResults = (results: any) => {
    const lineItems = []
    const roofArea = results.results?.roof_area_sqft || 0
    const materials = results.results?.materials || []

    materials.forEach((material: any, index: number) => {
      lineItems.push({
        category: "MATERIAL",
        description: material.type || material,
        quantity: roofArea,
        unit: "sq ft",
        unitCost: 0,
        totalCost: 0,
        confidence: 0.9,
        sourceReference: "Pipeline analysis",
      })
    })

    return lineItems
  }

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

  // Mock data function removed - only for demo/testing purposes
  // Real data comes from pipeline processing results

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
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary rounded-xl shadow-sm">
                <Building2 className="h-7 w-7 text-primary-foreground" />
              </div>
              <div>
                <h1 className="font-bold text-2xl text-slate-900">Roofing Estimate</h1>
                <p className="text-base text-slate-600">{estimateData.projectInfo.name}</p>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              {dataSource && <Badge variant="secondary">Source: {dataSource}</Badge>}
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
