"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export function UploadZone() {
  const [files, setFiles] = useState<File[]>([])
  const [status, setStatus] = useState("")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setFiles(fileList);
    }
  }

  const handleUploadClick = () => {
    setStatus("Upload clicked");
    
    if (files.length === 0) {
      alert("No files selected");
      return;
    }
    
    // Try to upload
    doUpload();
  }

  const doUpload = async () => {
    setStatus("Uploading...");
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
      
      const response = await fetch(`${apiUrl}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      setStatus(`Success! Document ID: ${result.id}`);
      alert("Upload successful!");
      
    } catch (error) {
      console.error("Upload error:", error);
      setStatus(`Error: ${error.message}`);
      alert(`Upload failed: ${error.message}`);
    }
  }

  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl mb-4">Simple Upload Test</h2>
      
      <div className="space-y-4">
        <div>
          <input 
            type="file" 
            accept=".pdf"
            onChange={handleFileChange}
            className="mb-2"
          />
        </div>
        
        {files.length > 0 && (
          <div>
            <p>Selected: {files[0].name}</p>
            <p>Size: {(files[0].size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}
        
        <Button 
          onClick={handleUploadClick}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Test Upload
        </Button>
        
        <button 
          onClick={() => {}}
          className="bg-green-500 text-white px-4 py-2 rounded ml-2"
        >
          Test Console Log
        </button>
        
        {status && (
          <div className="mt-4 p-2 bg-gray-100 rounded">
            Status: {status}
          </div>
        )}
      </div>
    </div>
  )
}