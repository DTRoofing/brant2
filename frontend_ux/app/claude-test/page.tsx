'use client'

import React, { useState } from 'react'
import { Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { FinalEstimateDisplay } from '../components/FinalEstimateDisplay'

interface FinalEstimateResponse {
  total_area_sqft: number;
  estimated_cost: number;
  materials_needed: any[];
  labor_estimate: any;
  timeline_estimate: string;
  confidence_score: number;
  processing_metadata: any;
  document_info: any;
}

export default function ClaudeTestPage() {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [estimateData, setEstimateData] = useState<FinalEstimateResponse | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setStatus('idle')
      setMessage('')
      setEstimateData(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file first')
      return
    }

    setIsUploading(true)
    setStatus('uploading')
    setUploadProgress(0)
    setEstimateData(null)
    setMessage('Uploading document...')

    try {
      // --- Step 1: Upload with progress tracking using XMLHttpRequest ---
      const docId = await new Promise<string>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', 'claude_direct_test');
        formData.append('project_id', `claude-test-${new Date().getTime()}`);

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(percentComplete);
            setMessage(`Uploading... ${percentComplete}%`);
          }
        };

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const uploadData = JSON.parse(xhr.responseText);
            resolve(uploadData.document_id);
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(`Upload failed: ${errorData.detail || xhr.statusText}`));
            } catch {
              reject(new Error(`Upload failed with status: ${xhr.statusText}`));
            }
          }
        };

        xhr.onerror = () => {
          reject(new Error('Upload failed due to a network error.'));
        };

        xhr.open('POST', '/api/proxy/documents/upload', true);
        xhr.send(formData);
      });

      setDocumentId(docId)
      setMessage('Upload complete. Queueing for processing...')
      setStatus('processing')

      // --- Step 2: Queue the processing task ---
      const processResponse = await fetch('/api/proxy/pipeline/process-with-claude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: docId }),
      })

      if (processResponse.status !== 202) {
        const errorData = await processResponse.json().catch(() => ({ detail: processResponse.statusText }))
        throw new Error(`Processing failed: ${errorData.detail}`)
      }

      const taskData = await processResponse.json()
      const taskId = taskData.task_id

      // --- Step 3: Poll for status ---
      setMessage(`Processing... Status: PENDING`);
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`/api/proxy/pipeline/status/${taskId}`)
          if (!statusResponse.ok) return;

          const statusData = await statusResponse.json();
          if (statusData.status !== 'SUCCESS' && statusData.status !== 'FAILURE') {
            setMessage(`Processing... Status: ${statusData.status}`);
          }

          if (statusData.status === 'SUCCESS') {
            clearInterval(pollInterval);
            setMessage('Processing complete! Fetching final estimate...');
            
            const estimateResponse = await fetch(`/api/proxy/pipeline/estimate/${docId}`);
            if (estimateResponse.ok) {
              const finalEstimate = await estimateResponse.json();
              setEstimateData(finalEstimate);
              setStatus('success');
              setMessage('Estimate generated successfully!');
            } else {
              const errorData = await estimateResponse.json().catch(() => ({ detail: 'Failed to fetch estimate.' }));
              throw new Error(errorData.detail);
            }
            setIsUploading(false);
          } else if (statusData.status === 'FAILURE') {
            clearInterval(pollInterval);
            throw new Error(statusData.error || 'An unknown processing error occurred.');
          }
        } catch (pollError) {
          clearInterval(pollInterval);
          // To avoid overwriting the original error, we'll just log this one
          // and let the main catch block handle the user-facing message.
          console.error("Polling failed:", pollError);
          // We re-throw the original error from the catch block below
          throw new Error("Polling failed. Please check the console for details.");
        }
      }, 3000);

    } catch (error) {
      console.error('Error:', error)
      setStatus('error')
      setMessage(error instanceof Error ? error.message : 'An error occurred during processing')
      setIsUploading(false)
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-500" />
      default:
        return <Upload className="w-6 h-6 text-gray-400" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Direct-to-Claude Pipeline</h1>
        <p className="text-gray-600 mb-8">
          Upload a roofing document to process it with Claude AI and generate an estimate
        </p>

        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Upload Area */}
          <div className="mb-6">
            <label
              htmlFor="file-upload"
              className="block w-full cursor-pointer"
            >
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors">
                <div className="flex justify-center mb-4">
                  {getStatusIcon()}
                </div>

                <p className="text-lg font-medium text-gray-700 mb-2">
                  {file ? file.name : 'Click to select a document'}
                </p>

                <p className="text-sm text-gray-500">
                  PDF files up to 120MB
                </p>

                {status === 'uploading' && (
                  <div className="w-full bg-gray-200 rounded-full h-2.5 mt-4">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                )}

                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept=".pdf"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </div>
            </label>
          </div>

          {/* Status Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg ${
              status === 'error' ? 'bg-red-50 text-red-700' :
              status === 'success' ? 'bg-green-50 text-green-700' :
              'bg-blue-50 text-blue-700'
            }`}>
              <p className="font-medium">{message}</p>
              {documentId && (
                <p className="text-sm mt-1">Document ID: {documentId}</p>
              )}
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className={`w-full py-3 px-6 rounded-lg font-medium transition-all ${
              !file || isUploading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-98'
            }`}
          >
            {isUploading ? 'Processing...' : 'Upload and Process with Claude'}
          </button>

          {/* Processing Steps */}
          {status !== 'idle' && (
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="font-medium text-gray-900 mb-4">Processing Steps:</h3>
              <div className="space-y-3">
                <div className={`flex items-center ${
                  ['uploading', 'processing', 'success'].includes(status) ? 'text-green-600' : 'text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-3 ${
                    ['uploading', 'processing', 'success'].includes(status) ? 'bg-green-600' : 'bg-gray-300'
                  }`} />
                  <span>Upload document</span>
                </div>

              </div>
            </div>
          )}
        </div>

        {/* Test Instructions */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="font-medium text-blue-900 mb-2">How it works:</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>Select a PDF roofing document (blueprints, estimates, or inspection reports)</li>
            <li>Click "Upload and Process with Claude" to start</li>
            <li>The document will be uploaded and processed by Claude AI</li>
            <li>You'll be automatically redirected to the estimate page with results</li>
          </ol>
        </div>
      </div>
    </div>
  )
}