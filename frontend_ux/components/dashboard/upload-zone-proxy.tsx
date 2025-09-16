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

  const testBackendConnection = async () => {
    console.log("Testing backend connection via proxy...");
    setStatus("Testing backend via proxy...");
    
    try {
      const response = await fetch('/api/proxy/health');
      console.log("Health check response:", response.status);
      const data = await response.text();
      console.log("Health check data:", data);
      setStatus(`Backend connected via proxy: ${data}`);
    } catch (error) {
      console.error("Backend test failed:", error);
      setStatus(`Backend connection failed: ${error.message}`);
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
    
    doUpload();
  }

  const doUpload = async () => {
    console.log("Starting upload via proxy...");
    setStatus("Uploading via proxy...");
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      console.log("Sending request to proxy:", '/api/proxy/documents/upload');
      console.log("FormData has file:", formData.has('file'));
      
      const response = await fetch('/api/proxy/documents/upload', {
        method: 'POST',
        body: formData
      });
      
      console.log("Response received:", response);
      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log("Error response body:", errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const result = await response.json();
      console.log("Response data:", result);
      
      setStatus(`Success! Document ID: ${result.id}`);
      alert("Upload successful via proxy!");
      
    } catch (error) {
      console.error("Upload error:", error);
      console.error("Error type:", error.name);
      console.error("Error message:", error.message);
      setStatus(`Error: ${error.message}`);
      alert(`Upload failed: ${error.message}`);
    }
  }

  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl mb-4">Upload Test with Proxy</h2>
      
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
        
        <div className="flex gap-2">
          <Button 
            onClick={testBackendConnection}
            className="bg-yellow-500 text-white px-4 py-2 rounded"
          >
            Test Backend via Proxy
          </Button>
          
          <Button 
            onClick={handleUploadClick}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Upload via Proxy
          </Button>
          
          <button 
            onClick={() => console.log("Plain button clicked")}
            className="bg-green-500 text-white px-4 py-2 rounded"
          >
            Test Console Log
          </button>
        </div>
        
        {status && (
          <div className="mt-4 p-2 bg-gray-100 rounded">
            Status: {status}
          </div>
        )}
      </div>
    </div>
  )
}