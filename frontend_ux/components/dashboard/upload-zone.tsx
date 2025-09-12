"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X } from "lucide-react"
import { cn } from "@/lib/utils"

export function UploadZone() {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState<File[]>([])

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
      const newFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === "application/pdf")
      setFiles((prev) => [...prev, ...newFiles])
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter((file) => file.type === "application/pdf")
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleUpload = async () => {
    if (files.length > 0) {
      setUploading(true)
      setUploadProgress(0)
      
      try {
        // Import the API client
        const { apiClient } = await import('@/lib/api');
        
        // Upload each file
        const uploadedDocs = []
        for (let i = 0; i < files.length; i++) {
          const file = files[i]
          setUploadProgress((i / files.length) * 100)
          
          const result = await apiClient.uploadDocument(file);
          console.log('Uploaded:', result);
          console.log('Document will be processed with:');
          console.log('- Google Document AI for text extraction');
          console.log('- Google Cloud Storage for backup');
          console.log('- Claude AI for measurement analysis');
          
          uploadedDocs.push(result);
        }
        
        // Store document IDs in localStorage for processing page
        const existingDocs = JSON.parse(localStorage.getItem('uploadedDocuments') || '[]');
        localStorage.setItem('uploadedDocuments', JSON.stringify([...existingDocs, ...uploadedDocs]));
        
        setUploadProgress(100)
        
        // Show success message
        alert(`Successfully uploaded ${files.length} file(s). Google Document AI will now process them.`);
        
        // Navigate to processing page
        setTimeout(() => {
          window.location.href = "/processing"
        }, 1000)
      } catch (error) {
        console.error('Upload failed:', error);
        alert('Failed to upload files. Please try again.');
      } finally {
        setUploading(false)
        setUploadProgress(0)
      }
    }
  }

  return (
    <div className="space-y-4">
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
          type="file"
          multiple
          accept=".pdf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
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
          </div>

          <Button variant="outline">Choose Files</Button>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium">Selected Files ({files.length})</h4>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => removeFile(index)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          <Button onClick={handleUpload} className="w-full" disabled={uploading}>
            {uploading ? (
              <>Processing with Google Document AI... {uploadProgress.toFixed(0)}%</>
            ) : (
              <>Process {files.length} Document{files.length !== 1 ? "s" : ""} with Google AI</>
            )}
          </Button>
          {uploading && (
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${uploadProgress}%` }}></div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
