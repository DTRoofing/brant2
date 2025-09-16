"use client"

import type React from "react"
import { useState, useCallback, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
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
  Clock,
  Loader2
} from "lucide-react"
import { cn } from "@/lib/utils"

interface UnifiedUploadProps {
  title?: string
  description?: string
  showPipelineStages?: boolean
  onUploadComplete?: (documentId: string, results?: any) => void
  redirectToEstimate?: boolean
  redirectToProcessing?: boolean
  className?: string
}

interface ProcessingStage {
  id: string
  title: string
  description: string
  icon: React.ElementType
  status: "pending" | "processing" | "completed" | "error"
  progress: number
}

export function UnifiedUpload({
  title = "Upload PDF Document",
  description = "Upload roofing documents for AI-powered processing and estimation",
  showPipelineStages = false,
  onUploadComplete,
  redirectToEstimate = false,
  redirectToProcessing = true,
  className
}: UnifiedUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [status, setStatus] = useState("")
  const [statusType, setStatusType] = useState<"info" | "success" | "error">("info")
  const [currentStage, setCurrentStage] = useState<number>(-1)
  const [documentId, setDocumentId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const processingStages: ProcessingStage[] = [
    {
      id: "upload",
      title: "Document Upload",
      description: "Uploading and validating PDF",
      icon: Upload,
      status: "pending",
      progress: 0
    },
    {
      id: "document_analysis",
      title: "Document Analysis",
      description: "Analyzing document type",
      icon: Brain,
      status: "pending",
      progress: 0
    },
    {
      id: "content_extraction",
      title: "Content Extraction",
      description: "Extracting text and images",
      icon: Eye,
      status: "pending",
      progress: 0
    },
    {
      id: "roof_measurement",
      title: "Roof Measurement",
      description: "Detecting roof features",
      icon: Building2,
      status: "pending",
      progress: 0
    },
    {
      id: "ai_interpretation",
      title: "AI Interpretation",
      description: "Analyzing with Claude AI",
      icon: Zap,
      status: "pending",
      progress: 0
    },
    {
      id: "estimate_generation",
      title: "Estimate Generation",
      description: "Creating estimate",
      icon: Calculator,
      status: "pending",
      progress: 0
    }
  ]

  const [stages, setStages] = useState<ProcessingStage[]>(processingStages)

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
      const newFiles = Array.from(e.dataTransfer.files).filter(
        (file) => file.type === "application/pdf"
      )
      setFiles((prev) => [...prev, ...newFiles])
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter(
        (file) => file.type === "application/pdf"
      )
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const updateStage = (stageIndex: number, status: ProcessingStage["status"], progress: number) => {
    setStages(prev => prev.map((stage, i) => 
      i === stageIndex ? { ...stage, status, progress } : stage
    ))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setStatus("Please select a file first")
      setStatusType("error")
      return
    }

    setUploading(true)
    setProcessing(false)
    setUploadProgress(0)
    setStatus("Uploading document...")
    setStatusType("info")
    setCurrentStage(0)
    
    // Reset stages
    setStages(processingStages)
    
    try {
      const formData = new FormData()
      formData.append('file', files[0])
      
      // Update first stage
      if (showPipelineStages) {
        updateStage(0, "processing", 50)
      }
      
      // Use the proxy endpoint for upload
      const response = await fetch('/api/proxy/documents/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Upload failed: ${response.status}`)
      }
      
      const result = await response.json()
      const docId = result.id || result.document_id
      setDocumentId(docId)
      
      // Update upload stage to completed
      if (showPipelineStages) {
        updateStage(0, "completed", 100)
      }
      
      setUploadProgress(100)
      setStatus(`Document uploaded successfully! ID: ${docId}`)
      setStatusType("success")
      setUploading(false)
      setProcessing(true)
      
      // Start processing pipeline
      await startProcessing(docId)
      
    } catch (error: any) {
      console.error("Upload error:", error)
      setUploading(false)
      setProcessing(false)
      
      if (showPipelineStages && currentStage >= 0) {
        updateStage(currentStage, "error", 0)
      }
      
      if (error.name === 'AbortError') {
        setStatus("Upload timed out. Please try again.")
        setStatusType("error")
      } else if (error.message.includes('413')) {
        setStatus("File too large. Maximum size is 200MB.")
        setStatusType("error")
      } else if (error.message.includes('Failed to fetch')) {
        setStatus("Connection error. Please check if the server is running.")
        setStatusType("error")
      } else {
        setStatus(`Error: ${error.message}`)
        setStatusType("error")
      }
    }
  }

  const startProcessing = async (docId: string) => {
    try {
      setStatus("Starting processing pipeline...")
      setStatusType("info")
      setCurrentStage(1)
      
      if (showPipelineStages) {
        updateStage(1, "processing", 0)
      }
      
      // Start pipeline processing
      const processResponse = await fetch(`/api/proxy/pipeline/process/${docId}`, {
        method: 'POST'
      })
      
      if (!processResponse.ok) {
        throw new Error(`Failed to start processing: ${processResponse.status}`)
      }
      
      const processData = await processResponse.json()
      const taskId = processData.task_id
      
      setStatus(`Processing started (Task: ${taskId})`)
      setStatusType("info")
      
      // Monitor processing
      await monitorProcessing(docId)
      
    } catch (error: any) {
      console.error("Processing error:", error)
      setProcessing(false)
      setStatus(`Processing error: ${error.message}`)
      setStatusType("error")
      
      if (showPipelineStages && currentStage >= 0) {
        updateStage(currentStage, "error", 0)
      }
    }
  }

  const monitorProcessing = async (docId: string) => {
    const maxWaitTime = 300000 // 5 minutes
    const startTime = Date.now()
    let stageProgress = 1
    
    while (Date.now() - startTime < maxWaitTime) {
      try {
        const statusResponse = await fetch(`/api/proxy/pipeline/status/${docId}`)
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json()
          const currentStatus = statusData.status
          
          if (currentStatus === 'completed') {
            // Update all stages to completed
            if (showPipelineStages) {
              for (let i = 1; i < stages.length; i++) {
                updateStage(i, "completed", 100)
                await new Promise(resolve => setTimeout(resolve, 200))
              }
            }
            
            setStatus("Processing completed successfully!")
            setStatusType("success")
            setProcessing(false)
            
            // Get results
            const resultsResponse = await fetch(`/api/proxy/pipeline/results/${docId}`)
            if (resultsResponse.ok) {
              const results = await resultsResponse.json()
              
              // Call callback if provided
              if (onUploadComplete) {
                onUploadComplete(docId, results)
              }
              
              // Redirect based on settings
              if (redirectToProcessing) {
                setTimeout(() => {
                  window.location.href = `/processing?documents=${docId}`
                }, 1000)
              } else if (redirectToEstimate) {
                setTimeout(() => {
                  window.location.href = `/estimate?source=pipeline&documentId=${docId}`
                }, 1000)
              }
            }
            
            break
            
          } else if (currentStatus === 'failed') {
            const error = statusData.error || 'Unknown error'
            setStatus(`Processing failed: ${error}`)
            setStatusType("error")
            setProcessing(false)
            
            if (showPipelineStages && currentStage >= 0) {
              updateStage(currentStage, "error", 0)
            }
            break
            
          } else {
            // Update stages progressively during processing
            if (showPipelineStages && stageProgress < stages.length - 1) {
              updateStage(stageProgress, "completed", 100)
              stageProgress++
              if (stageProgress < stages.length) {
                updateStage(stageProgress, "processing", 50)
                setCurrentStage(stageProgress)
              }
            }
            
            setStatus(`Processing... (${Math.floor((Date.now() - startTime) / 1000)}s)`)
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000))
        
      } catch (error: any) {
        console.error("Status check error:", error)
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }
    
    if (processing) {
      setStatus("Processing timeout - please check status manually")
      setStatusType("error")
      setProcessing(false)
    }
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      {(title || description) && (
        <div>
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
        </div>
      )}

      {/* Drop Zone */}
      <div
        className={cn(
          "relative rounded-lg border-2 border-dashed p-8 transition-colors",
          dragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50",
          files.length > 0 && "pb-4",
          (uploading || processing) && "opacity-50 pointer-events-none"
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
          accept="application/pdf"
          onChange={handleFileInput}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          disabled={uploading || processing}
        />
        
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="rounded-full bg-muted p-4">
            <Upload className="h-8 w-8 text-muted-foreground" />
          </div>
          
          <div>
            <p className="text-lg font-medium">Drop your PDF files here</p>
            <p className="mt-1 text-sm text-muted-foreground">
              or click to browse from your computer
            </p>
          </div>
          
          <p className="text-xs text-muted-foreground">
            Only PDF files are accepted (Max 200MB)
          </p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && !uploading && !processing && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between rounded-lg border bg-card p-3"
            >
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFile(index)}
                disabled={uploading || processing}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Processing Stages */}
      {showPipelineStages && (uploading || processing) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Processing Pipeline</CardTitle>
            <CardDescription>
              Hybrid AI processing for maximum accuracy
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {stages.map((stage, index) => (
              <div key={stage.id} className="flex items-start gap-3">
                <div className={cn(
                  "p-2 rounded-lg transition-colors",
                  stage.status === "completed" && "bg-green-100",
                  stage.status === "processing" && "bg-blue-100",
                  stage.status === "error" && "bg-red-100",
                  stage.status === "pending" && "bg-gray-100"
                )}>
                  {stage.status === "processing" ? (
                    <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  ) : stage.status === "completed" ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : stage.status === "error" ? (
                    <AlertCircle className="h-4 w-4 text-red-600" />
                  ) : (
                    <stage.icon className="h-4 w-4 text-gray-400" />
                  )}
                </div>
                <div className="flex-1">
                  <h4 className={cn(
                    "font-medium text-sm",
                    stage.status === "pending" && "text-muted-foreground"
                  )}>
                    {stage.title}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stage.description}
                  </p>
                  {stage.status === "processing" && (
                    <Progress value={stage.progress} className="h-1 mt-2" />
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Upload Button and Progress */}
      {files.length > 0 && !processing && (
        <div className="space-y-2">
          <Button
            onClick={handleUpload}
            disabled={uploading || processing}
            className="w-full"
            size="lg"
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading... {uploadProgress.toFixed(0)}%
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload and Process {files.length} {files.length === 1 ? 'File' : 'Files'}
              </>
            )}
          </Button>
          
          {uploading && (
            <Progress value={uploadProgress} className="h-2" />
          )}
        </div>
      )}

      {/* Status Message */}
      {status && (
        <Alert className={cn(
          statusType === "error" && "border-destructive",
          statusType === "success" && "border-green-500",
          statusType === "info" && "border-blue-500"
        )}>
          <AlertDescription className={cn(
            statusType === "error" && "text-destructive",
            statusType === "success" && "text-green-600",
            statusType === "info" && "text-blue-600"
          )}>
            {status}
          </AlertDescription>
        </Alert>
      )}

      {/* Processing Indicator */}
      {processing && !showPipelineStages && (
        <div className="flex items-center justify-center p-4">
          <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
          <span className="text-sm font-medium">Processing document...</span>
        </div>
      )}
    </div>
  )
}