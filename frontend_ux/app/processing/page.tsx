"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, Bot, Eye, Zap, Clock, Building2, Calculator, AlertTriangle } from "lucide-react"
import { ProcessingStage } from "@/components/processing/processing-stage"
import { ExtractedDataPreview } from "@/components/processing/extracted-data-preview"

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
  const [sqftExtractionFailed, setSqftExtractionFailed] = useState(false) // Added state for tracking square footage extraction failure

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
      id: "ocr",
      title: "Google Document AI",
      description: "Extracting text and structural data from documents",
      icon: Bot,
      status: "processing",
      progress: 0,
      duration: 8000,
    },
    {
      id: "vision",
      title: "Cloud Vision Analysis",
      description: "Analyzing blueprints, measurements, and visual elements",
      icon: Eye,
      status: "pending",
      progress: 0,
      duration: 6000,
    },
    {
      id: "extraction",
      title: "Data Extraction",
      description: "Identifying materials, measurements, and specifications",
      icon: Zap,
      status: "pending",
      progress: 0,
      duration: 5000,
    },
    {
      id: "analysis",
      title: "Roofing Analysis",
      description: "Calculating costs, labor, and project requirements",
      icon: Calculator,
      status: "pending",
      progress: 0,
      duration: 4000,
    },
  ]

  const [steps, setSteps] = useState(processingSteps)

  useEffect(() => {
    const processSteps = async () => {
      for (let i = 0; i < steps.length; i++) {
        if (i > 0) {
          // Mark previous step as completed
          setSteps((prev) =>
            prev.map((step, index) =>
              index === i - 1 ? { ...step, status: "completed" as const, progress: 100 } : step,
            ),
          )
        }

        // Start current step
        setCurrentStep(i)
        setSteps((prev) => prev.map((step, index) => (index === i ? { ...step, status: "processing" as const } : step)))

        // Simulate progress for current step
        const stepDuration = steps[i].duration
        const progressInterval = stepDuration / 100

        for (let progress = 0; progress <= 100; progress += 2) {
          await new Promise((resolve) => setTimeout(resolve, progressInterval))

          setSteps((prev) => prev.map((step, index) => (index === i ? { ...step, progress } : step)))

          // Update overall progress
          const completedSteps = i * 100
          const currentStepProgress = progress
          const totalProgress = (completedSteps + currentStepProgress) / steps.length
          setOverallProgress(totalProgress)

          // Add extracted data during processing
          if (i === 1 && progress > 30) {
            // Document AI step
            setExtractedData((prev) => {
              if (prev.length === 0) {
                return [
                  { type: "Building Type", value: "Commercial Warehouse", confidence: 98 },
                  { type: "Square Footage", value: "Unable to determine from PDF", confidence: 0 }, // Simulate square footage extraction failure in some cases
                ]
              }
              return prev
            })
            setSqftExtractionFailed(true)
          }

          if (i === 2 && progress > 50) {
            // Vision step
            setExtractedData((prev) => [
              ...prev,
              { type: "Roof Material", value: "TPO Membrane", confidence: 92 },
              { type: "Slope", value: "1/4 inch per foot", confidence: 89 },
            ])
          }

          if (i === 3 && progress > 40) {
            // Extraction step
            setExtractedData((prev) => [
              ...prev,
              { type: "Insulation", value: "R-30 Polyiso", confidence: 94 },
              { type: "Drainage", value: "Internal drains (8)", confidence: 91 },
            ])
          }
        }
      }

      // All steps completed
      setSteps((prev) => prev.map((step) => ({ ...step, status: "completed" as const, progress: 100 })))
      setOverallProgress(100)

      // Redirect to results after a brief delay
      setTimeout(() => {
        window.location.href = "/estimate"
      }, 2000)
    }

    processSteps()
  }, [])

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

          {/* Action Buttons */}
          <div className="flex justify-center gap-4">
            <Button variant="outline" disabled={overallProgress < 100}>
              <Clock className="h-4 w-4 mr-2" />
              {overallProgress < 100 ? "Processing..." : "View Results"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
