"use client"

import type React from "react"
import { useState, useCallback, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Brain, 
  Eye, 
  Zap, 
  Calculator,
  Building2,
  Clock
} from "lucide-react"
import { cn } from "@/lib/utils"

interface ProcessingStage {
  id: string
  title: string
  description: string
  icon: React.ElementType
  status: "pending" | "processing" | "completed" | "error"
  progress: number
}

interface UploadedFile {
  file: File
  id: string
  status: "uploading" | "processing" | "completed" | "error"
  progress: number
  result?: any
  error?: string
}

export function PDFPipelineUpload() {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [currentStage, setCurrentStage] = useState(0)
  const [pipelineResults, setPipelineResults] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const processingStages: ProcessingStage[] = [
    {
      id: "upload",
      title: "Document Upload",
      description: "Securing and validating PDF documents",
      icon: Upload,
      status: "pending",
      progress: 0
    },
    {
      id: "document_analysis",
      title: "Document Analysis",
      description: "Classifying document type and determining processing strategy",
      icon: Brain,
      status: "pending",
      progress: 0
    },
    {
      id: "content_extraction",
      title: "Hybrid Content Extraction",
      description: "Computer vision + AI extraction of text, images, and measurements",
      icon: Eye,
      status: "pending",
      progress: 0
    },
    {
      id: "roof_measurement",
      title: "Roof Measurement",
      description: "Scale detection and roof feature identification",
      icon: Building2,
      status: "pending",
      progress: 0
    },
    {
      id: "ai_interpretation",
      title: "AI Interpretation",
      description: "Claude AI analysis and cost estimation",
      icon: Zap,
      status: "pending",
      progress: 0
    },
    {
      id: "estimate_generation",
      title: "Estimate Generation",
      description: "Generating comprehensive roofing estimate",
      icon: Calculator,
      status: "pending",
      progress: 0
    }
  ]

  const [stages, setStages] = useState(processingStages)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files)
        .filter((file) => file.type === "application/pdf")
        .map((file) => ({
          file,
          id: Math.random().toString(36).substr(2, 9),
          status: "uploading" as const,
          progress: 0
        }))
      
      setFiles(prev => [...prev, ...newFiles])
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files)
        .filter((file) => file.type === "application/pdf")
        .map((file) => ({
          file,
          id: Math.random().toString(36).substr(2, 9),
          status: "uploading" as const,
          progress: 0
        }))
      
      setFiles(prev => [...prev, ...newFiles])
    }
  }

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id))
  }

  const uploadAndProcess = async () => {
    if (files.length === 0) return

    setIsUploading(true)
    setCurrentStage(0)

    try {
      // Import API client
      const { apiClient } = await import('@/lib/api')

      // Process each file
      for (let i = 0; i < files.length; i++) {
        const fileData = files[i]
        
        // Update file status
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: "uploading", progress: 0 }
            : f
        ))

        // Stage 1: Upload
        updateStage(0, "processing", 0)
        const uploadResult = await apiClient.uploadDocument(fileData.file)
        
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: "processing", progress: 25, result: uploadResult }
            : f
        ))

        // Stage 2: Start Pipeline
        updateStage(1, "processing", 0)
        const pipelineResult = await apiClient.startPipelineProcessing(uploadResult.document_id)
        
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, progress: 50, result: { ...f.result, pipeline: pipelineResult } }
            : f
        ))

        // Stage 3: Monitor Pipeline
        updateStage(2, "processing", 0)
        const results = await monitorPipeline(uploadResult.document_id)
        
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: "completed", progress: 100, result: { ...f.result, results } }
            : f
        ))

        // Complete all stages
        completeAllStages()
      }

      // Store results for estimate page
      const completedFiles = files.filter(f => f.status === "completed")
      if (completedFiles.length > 0) {
        const latestResult = completedFiles[completedFiles.length - 1].result
        localStorage.setItem('latestPipelineResults', JSON.stringify(latestResult))
        
        // Redirect to estimate page
        setTimeout(() => {
          window.location.href = `/estimate?source=pipeline&documentId=${latestResult.document_id}`
        }, 2000)
      }

    } catch (error) {
      console.error('Pipeline processing failed:', error)
      setFiles(prev => prev.map(f => ({ ...f, status: "error", error: error.message })))
      updateStage(currentStage, "error", 0)
    } finally {
      setIsUploading(false)
    }
  }

  const monitorPipeline = async (documentId: string) => {
    const maxWaitTime = 300000 // 5 minutes
    const startTime = Date.now()
    
    while (Date.now() - startTime < maxWaitTime) {
      try {
        const status = await apiClient.getPipelineStatus(documentId)
        
        // Update stages based on status
        if (status.status === 'processing') {
          updateStage(2, "processing", 50)
          updateStage(3, "processing", 25)
        } else if (status.status === 'completed') {
          updateStage(2, "completed", 100)
          updateStage(3, "completed", 100)
          updateStage(4, "completed", 100)
          updateStage(5, "completed", 100)
          
          const results = await apiClient.getPipelineResults(documentId)
          return results
        } else if (status.status === 'failed') {
          throw new Error(`Pipeline failed: ${status.error}`)
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000))
      } catch (error) {
        console.error('Error monitoring pipeline:', error)
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }
    
    throw new Error('Pipeline processing timeout')
  }

  const updateStage = (stageIndex: number, status: "pending" | "processing" | "completed" | "error", progress: number) => {
    setStages(prev => prev.map((stage, index) => 
      index === stageIndex 
        ? { ...stage, status, progress }
        : stage
    ))
    setCurrentStage(stageIndex)
  }

  const completeAllStages = () => {
    setStages(prev => prev.map(stage => ({ ...stage, status: "completed", progress: 100 })))
  }

  const getStageIcon = (stage: ProcessingStage) => {
    const Icon = stage.icon
    if (stage.status === "completed") return <CheckCircle className="h-5 w-5 text-green-600" />
    if (stage.status === "error") return <AlertCircle className="h-5 w-5 text-red-600" />
    if (stage.status === "processing") return <Clock className="h-5 w-5 text-blue-600 animate-spin" />
    return <Icon className="h-5 w-5 text-gray-400" />
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800"
      case "processing": return "bg-blue-100 text-blue-800"
      case "error": return "bg-red-100 text-red-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-primary" />
            PDF Pipeline Upload
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
              dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50",
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              aria-label="Upload PDF files"
            />

            <div className="flex flex-col items-center gap-4">
              <div className="p-4 bg-primary/10 rounded-full">
                <Upload className="h-8 w-8 text-primary" />
              </div>

              <div className="space-y-2">
                <h3 className="text-lg font-semibold">Upload Roofing Documents</h3>
                <p className="text-muted-foreground">Drag and drop PDF files here, or click to browse</p>
                <p className="text-sm text-muted-foreground">
                  Supports: Blueprints, Specifications, Site Plans, Material Lists
                </p>
                <div className="flex items-center gap-2 text-sm text-primary">
                  <Brain className="h-4 w-4" />
                  <span>Hybrid AI + Computer Vision Processing</span>
                </div>
              </div>

              <Button 
                variant="outline" 
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                Choose Files
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Files ({files.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {files.map((fileData) => (
              <div key={fileData.id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{fileData.file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <Badge className={cn("text-xs", getStatusColor(fileData.status))}>
                      {fileData.status}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {fileData.progress > 0 && (
                    <div className="w-20">
                      <Progress value={fileData.progress} className="h-2" />
                    </div>
                  )}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => removeFile(fileData.id)}
                    disabled={isUploading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}

            <Button 
              onClick={uploadAndProcess} 
              className="w-full" 
              disabled={isUploading}
              size="lg"
            >
              {isUploading ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Processing with Hybrid Pipeline... {Math.round(files.reduce((acc, f) => acc + f.progress, 0) / files.length)}%
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Process {files.length} Document{files.length !== 1 ? "s" : ""} with Hybrid Pipeline
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Processing Stages */}
      {isUploading && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              Hybrid Pipeline Processing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {stages.map((stage, index) => (
              <div key={stage.id} className="flex items-center gap-4 p-3 rounded-lg bg-muted/50">
                <div className="flex-shrink-0">
                  {getStageIcon(stage)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium">{stage.title}</h4>
                    <Badge className={cn("text-xs", getStatusColor(stage.status))}>
                      {stage.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{stage.description}</p>
                  {stage.status === "processing" && (
                    <div className="mt-2">
                      <Progress value={stage.progress} className="h-1" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Results Preview */}
      {pipelineResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Processing Complete
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Your document has been successfully processed! Redirecting to estimate page...
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
