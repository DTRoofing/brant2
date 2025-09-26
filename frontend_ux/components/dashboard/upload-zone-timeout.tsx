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

  const testBackendConnection = async () => {
    setStatus("Testing backend...");
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || `http://localhost:${process.env.API_HOST_PORT || '3001'}`;
      const response = await fetch(`${apiUrl}/api/v1/health`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      const data = await response.text();
      setStatus(`Backend connected: ${data}`);
    } catch (error) {
      console.error("Backend test failed:", error);
      setStatus(`Backend connection failed: ${error.message}`);
    }
  }

  const handleUploadClick = () => {
    setStatus("Upload clicked - check console");
    
    if (files.length === 0) {
      alert("No files selected");
      return;
    }
    
    doUpload();
  }

  const doUpload = async () => {
    setStatus("Uploading...");
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || `http://localhost:${process.env.API_HOST_PORT || '3001'}`;
      
      // Add timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 10000); // 10 second timeout
      
      const response = await fetch(`${apiUrl}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      }).catch(err => {
        console.error("Fetch error caught:", err);
        throw new Error(`Network error: ${err.message}`);
      });
      
      clearTimeout(timeoutId);
      
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const result = await response.json();
      
      setStatus(`Success! Document ID: ${result.id}`);
      alert("Upload successful!");
      
    } catch (error) {
      console.error("Upload error caught:", error);
      console.error("Error type:", error.name);
      console.error("Error message:", error.message);
      console.error("Error stack:", error.stack);
      
      if (error.name === 'AbortError') {
        setStatus("Upload timed out after 10 seconds");
        alert("Upload timed out - backend might not be accessible from browser");
      } else {
        setStatus(`Error: ${error.message}`);
        alert(`Upload failed: ${error.message}`);
      }
    }
  }

  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl mb-4">Upload Test with Debugging</h2>
      
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
            Test Backend Connection
          </Button>
          
          <Button 
            onClick={handleUploadClick}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Test Upload
          </Button>
          
          <button 
            onClick={() => {}}
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