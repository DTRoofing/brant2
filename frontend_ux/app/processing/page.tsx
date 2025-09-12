"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, Bot, Eye, Zap, Clock, Building2, Calculator, AlertTriangle, CheckCircle, XCircle } from "lucide-react"
import { ProcessingStage } from "@/components/processing/processing-stage"
import { ExtractedDataPreview } from "@/components/processing/extracted-data-preview"
import { apiClient } from "@/lib/api"

interface ProcessingStep {
  id: string
  title: string
  description: string
  icon: React.ElementType
  status: "pending" | "processing" | "completed"
  progress: number
  duration: number
}

export default function ProcessingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [overallProgress, setOverallProgress] = useState(0)
  const [extractedData, setExtractedData] = useState<any[]>([])
  const [sqftExtractionFailed, setSqftExtractionFailed] = useState(false)
  const [documentIds, setDocumentIds] = useState<string[]>([])
  const [pipelineResults, setPipelineResults] = useState<any>(null)
  const [processingError, setProcessingError] = useState<string | null>(null)
  const [isCompleted, setIsCompleted] = useState(false)

  const processingSteps: ProcessingStep[] = [
    {
      id: "upload",
      title: "Document Upload",
      description: "Securing and validating PDF documents",
      icon: FileText,
      status: "completed",
      progress: 100,
      duration: 2000,
    },
    {
      id: "document_analysis",
      title: "Document Analysis",
      description: "Classifying document type and determining processing strategy",
      icon: Bot,
      status: "processing",
      progress: 0,
      duration: 3000,
    },
    {
      id: "content_extraction",
      title: "Content Extraction",
      description: "Extracting text, images, and measurements with hybrid approach",
      icon: Eye,
      status: "pending",
      progress: 0,
      duration: 8000,
    },
    {
      id: "ai_interpretation",
      title: "AI Interpretation",
      description: "Analyzing content with Claude AI and roof feature detection",
      icon: Zap,
      status: "pending",
      progress: 0,
      duration: 6000,
    },
    {
      id: "data_validation",
      title: "Data Validation",
      description: "Validating measurements and generating final estimate",
      icon: Calculator,
      status: "pending",
      progress: 0,
      duration: 4000,
    },
  ]

  const [steps, setSteps] = useState(processingSteps)

  useEffect(() => {
    // Get document IDs from URL parameters
    const urlParams = new URLSearchParams(window.location.search)
    const documentsParam = urlParams.get('documents')
    if (documentsParam) {
      setDocumentIds(documentsParam.split(','))
    }

    // If no document IDs, try to get from localStorage
    if (documentIds.length === 0) {
      const storedDocs = JSON.parse(localStorage.getItem('processedDocuments') || '[]')
      if (storedDocs.length > 0) {
        setDocumentIds(storedDocs.map((doc: any) => doc.document_id))
      }
    }
  }, [])

  useEffect(() => {
    if (documentIds.length === 0) return

    const monitorPipeline = async () => {
      try {
        // Monitor the first document (assuming single document processing for now)
        const documentId = documentIds[0]
        
        // Start monitoring with polling
        const pollInterval = setInterval(async () => {
          try {
            const status = await apiClient.getPipelineStatus(documentId)
            
            // Update steps based on status
            updateStepsFromStatus(status)
            
            // Check if completed
            if (status.status === 'completed') {
              clearInterval(pollInterval)
              const results = await apiClient.getPipelineResults(documentId)
              setPipelineResults(results)
              setIsCompleted(true)
              
              // Store results for estimate page
              localStorage.setItem('latestEstimateResults', JSON.stringify(results))
              
              // Redirect to estimate page after delay
              setTimeout(() => {
                window.location.href = `/estimate?source=pipeline&documentId=${documentId}`
              }, 2000)
            } else if (status.status === 'failed') {
              clearInterval(pollInterval)
              setProcessingError(status.error || 'Pipeline processing failed')
            }
          } catch (error) {
            console.error('Error monitoring pipeline:', error)
          }
        }, 2000) // Poll every 2 seconds

        // Cleanup on unmount
        return () => clearInterval(pollInterval)
      } catch (error) {
        console.error('Error starting pipeline monitoring:', error)
        setProcessingError('Failed to start pipeline monitoring')
      }
    }

    monitorPipeline()
  }, [documentIds])

  const updateStepsFromStatus = (status: any) => {
    // Map pipeline status to processing steps
    const stepMapping = {
      'pending': 0,
      'processing': 1,
      'completed': 4
    }

    const currentStepIndex = stepMapping[status.status as keyof typeof stepMapping] || 0
    setCurrentStep(currentStepIndex)

    // Update steps based on current status
    setSteps(prev => prev.map((step, index) => {
      if (index < currentStepIndex) {
        return { ...step, status: 'completed' as const, progress: 100 }
      } else if (index === currentStepIndex) {
        return { ...step, status: 'processing' as const, progress: 50 }
      } else {
        return { ...step, status: 'pending' as const, progress: 0 }
      }
    }))

    // Update overall progress
    const progress = (currentStepIndex / (steps.length - 1)) * 100
    setOverallProgress(progress)

    // Add extracted data based on pipeline results
    if (status.results) {
      const extracted = []
      
      if (status.results.roof_area_sqft) {
        extracted.push({
          type: "Roof Area",
          value: `${status.results.roof_area_sqft.toLocaleString()} sqft`,
          confidence: Math.round((status.results.confidence || 0.8) * 100)
        })
      }

      if (status.results.roof_features && status.results.roof_features.length > 0) {
        status.results.roof_features.forEach((feature: any) => {
          extracted.push({
            type: "Roof Feature",
            value: `${feature.type} (${feature.count || 1})`,
            confidence: Math.round((feature.confidence || 0.7) * 100)
          })
        })
      }

      if (status.results.materials && status.results.materials.length > 0) {
        status.results.materials.forEach((material: any) => {
          extracted.push({
            type: "Material",
            value: material.type || material,
            confidence: 90
          })
        })
      }

      setExtractedData(extracted)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-primary/5">
      {/* Header */}
      <div className="border-b bg-card/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Building2 className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Processing Documents</h1>
              <p className="text-sm text-muted-foreground">AI-powered analysis in progress</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Overall Progress */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-primary" />
                  AI Analysis Progress
                </CardTitle>
                <Badge variant="secondary" className="animate-pulse">
                  {overallProgress < 100 ? "Processing" : "Complete"}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span>Overall Progress</span>
                  <span>{Math.round(overallProgress)}%</span>
                </div>
                <Progress value={overallProgress} className="h-3" />
                <p className="text-sm text-muted-foreground">
                  Analyzing warehouse-roof-specs.pdf using Google Cloud AI services
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Processing Steps */}
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Processing Stages</h2>
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <ProcessingStage
                    key={step.id}
                    step={step}
                    isActive={currentStep === index}
                    isCompleted={step.status === "completed"}
                  />
                ))}
              </div>
            </div>

            {/* Extracted Data Preview */}
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Extracted Information</h2>
              <ExtractedDataPreview data={extractedData} />

              {sqftExtractionFailed && (
                <Card className="bg-orange-50 border-orange-200">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2 text-orange-800">
                      <AlertTriangle className="h-5 w-5" />
                      Manual Input Required
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-orange-700">
                      Square footage could not be determined from the PDF. You'll need to manually input this critical
                      measurement in the estimate review.
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* AI Services Info */}
              <Card className="bg-primary/5 border-primary/20">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Zap className="h-5 w-5 text-primary" />
                    AI Services Active
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                      <span>Document AI</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                      <span>Cloud Vision</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                      <span>Natural Language</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                      <span>AutoML Tables</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Error State */}
          {processingError && (
            <Card className="bg-red-50 border-red-200">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-red-800">
                  <XCircle className="h-5 w-5" />
                  Processing Error
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-red-700 mb-4">{processingError}</p>
                <Button 
                  variant="outline" 
                  onClick={() => window.location.href = '/dashboard'}
                  className="text-red-600 border-red-600 hover:bg-red-50"
                >
                  Return to Dashboard
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Completion State */}
          {isCompleted && (
            <Card className="bg-green-50 border-green-200">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-green-800">
                  <CheckCircle className="h-5 w-5" />
                  Processing Complete!
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-green-700 mb-4">
                  Your document has been successfully processed with the hybrid pipeline. 
                  Redirecting to estimate page...
                </p>
                <div className="flex gap-2">
                  <Button 
                    onClick={() => window.location.href = '/estimate'}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    View Estimate Now
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => window.location.href = '/dashboard'}
                  >
                    Return to Dashboard
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          {!processingError && !isCompleted && (
            <div className="flex justify-center gap-4">
              <Button variant="outline" disabled={overallProgress < 100}>
                <Clock className="h-4 w-4 mr-2" />
                {overallProgress < 100 ? "Processing..." : "View Results"}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
