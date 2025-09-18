"use client";

import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

interface SchematicUploadFormProps {
  onUploadComplete?: (documentId: string) => void;
  projectId?: string;
}

export function SchematicUploadForm({ onUploadComplete, projectId }: SchematicUploadFormProps) {
  const router = useRouter();
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "processing" | "complete" | "error">("idle");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [processingStage, setProcessingStage] = useState<string | null>(null);
  const [filePreview, setFilePreview] = useState<{ name: string; size: number } | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setFilePreview({ name: file.name, size: file.size });
    setErrorMessage(null);
    setUploadStatus("uploading");
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", "schematic");
    formData.append("processing_mode", "claude_yolo");
    if (projectId) {
      formData.append("project_id", projectId);
    }

    try {
      // Upload file
      const uploadResponse = await fetch("/api/proxy/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const uploadResult = await uploadResponse.json();
      const docId = uploadResult.document_id;
      setDocumentId(docId);
      setUploadStatus("processing");
      setUploadProgress(100);

      toast.success("File uploaded successfully");

      // Start processing with Claude/YOLO pipeline
      const processResponse = await fetch(`/api/v1/pipeline/process/${docId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          processing_mode: "claude_yolo",
          extract_visual_elements: true,
          extract_text_annotations: true,
          extract_measurements: true,
        }),
      });

      if (!processResponse.ok) {
        throw new Error(`Processing failed: ${processResponse.statusText}`);
      }

      // Poll for processing status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`/api/v1/pipeline/status/${docId}`);
          if (statusResponse.ok) {
            const status = await statusResponse.json();
            
            if (status.stage) {
              setProcessingStage(status.stage);
            }

            if (status.status === "completed") {
              clearInterval(pollInterval);
              setUploadStatus("complete");
              toast.success("Schematic processing complete!");
              
              if (onUploadComplete) {
                onUploadComplete(docId);
              } else {
                // Navigate to estimate page after 2 seconds
                setTimeout(() => {
                  router.push(`/estimate?documentId=${docId}`);
                }, 2000);
              }
            } else if (status.status === "failed") {
              clearInterval(pollInterval);
              throw new Error(status.error || "Processing failed");
            }
          }
        } catch (error) {
          clearInterval(pollInterval);
          console.error("Status polling error:", error);
          setUploadStatus("error");
          setErrorMessage("Failed to check processing status");
        }
      }, 2000);

    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "Upload failed");
      toast.error("Failed to upload file");
    }
  }, [projectId, router, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false,
  });

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case "uploading":
        return <Loader2 className="h-8 w-8 animate-spin text-blue-600" />;
      case "processing":
        return <Loader2 className="h-8 w-8 animate-spin text-purple-600" />;
      case "complete":
        return <CheckCircle className="h-8 w-8 text-green-600" />;
      case "error":
        return <AlertCircle className="h-8 w-8 text-red-600" />;
      default:
        return <Upload className="h-8 w-8 text-gray-400" />;
    }
  };

  const getProcessingStageDisplay = () => {
    const stages = {
      "claude_text_extraction": "Extracting text with Claude",
      "yolo_detection": "Detecting visual elements with YOLO",
      "measurement_extraction": "Extracting measurements",
      "data_synthesis": "Synthesizing data",
      "estimate_generation": "Generating estimate",
    };

    return stages[processingStage as keyof typeof stages] || processingStage;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload Schematic or Blueprint
        </CardTitle>
        <CardDescription>
          Upload PDF schematics or blueprints for AI-powered analysis using Claude and YOLO models
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-all duration-200 ease-in-out
            ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}
            ${uploadStatus !== "idle" ? "pointer-events-none opacity-50" : ""}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center gap-4">
            {getStatusIcon()}
            
            {uploadStatus === "idle" && (
              <>
                <div className="text-sm text-gray-600">
                  {isDragActive ? (
                    <p>Drop your schematic PDF here</p>
                  ) : (
                    <p>Drag and drop a schematic or blueprint PDF here, or click to select</p>
                  )}
                </div>
                <Button variant="secondary" size="sm">
                  Select File
                </Button>
                <div className="flex gap-2 mt-2">
                  <Badge variant="secondary">Claude Text Analysis</Badge>
                  <Badge variant="secondary">YOLO Visual Detection</Badge>
                </div>
              </>
            )}

            {uploadStatus === "uploading" && (
              <div className="w-full max-w-xs">
                <p className="text-sm text-gray-600 mb-2">Uploading {filePreview?.name}...</p>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}

            {uploadStatus === "processing" && (
              <div className="text-center">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Processing with AI Models
                </p>
                {processingStage && (
                  <p className="text-sm text-gray-600 mb-4">
                    {getProcessingStageDisplay()}
                  </p>
                )}
                <div className="flex gap-2 justify-center">
                  <Badge variant="default" className="animate-pulse">Claude Active</Badge>
                  <Badge variant="default" className="animate-pulse">YOLO Active</Badge>
                </div>
              </div>
            )}

            {uploadStatus === "complete" && (
              <div className="text-center">
                <p className="text-sm font-medium text-green-600 mb-2">
                  Analysis Complete!
                </p>
                <p className="text-xs text-gray-600">
                  Redirecting to estimate...
                </p>
                {documentId && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={() => router.push(`/estimate?documentId=${documentId}`)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    View Estimate
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>

        {errorMessage && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}

        {filePreview && uploadStatus !== "idle" && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700">
              {filePreview.name}
            </p>
            <p className="text-xs text-gray-500">
              {(filePreview.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}