"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export function UploadZone() {
  const [files, setFiles] = useState<File[]>([])
  const [status, setStatus] = useState("")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log("File input changed");
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      console.log("Files selected:", fileList);
      setFiles(fileList);
    }
  }

  const handleUploadClick = () => {
    console.log("Upload button clicked!");
    console.log("Current files:", files);
    setStatus("Upload clicked - check console");
    
    if (files.length === 0) {
      alert("No files selected");
      return;
    }
    
    // Try to upload
    doUpload();
  }

  const doUpload = async () => {
    console.log("Starting upload...");
    setStatus("Uploading...");
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      console.log("Sending request to:", 'http://localhost:3001/api/v1/documents/upload');
      
      const response = await fetch('http://localhost:3001/api/v1/documents/upload', {
        method: 'POST',
        body: formData
      });
      
      console.log("Response status:", response.status);
      const result = await response.json();
      console.log("Response data:", result);
      
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
          onClick={() => console.log("Plain button clicked")}
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