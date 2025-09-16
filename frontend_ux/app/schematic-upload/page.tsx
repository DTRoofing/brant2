"use client";

import React from "react";
import { SchematicUploadForm } from "@/components/dashboard/schematic-upload-form";
import { ArrowLeft, Info } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function SchematicUploadPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-6">
        <Link href="/upload">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Upload Options
          </Button>
        </Link>
        
        <h1 className="text-3xl font-bold mb-2">
          Schematic & Blueprint Analysis
        </h1>
        <p className="text-gray-600">
          Upload architectural schematics and blueprints for advanced AI analysis
        </p>
      </div>

      <Alert className="mb-6">
        <Info className="h-4 w-4" />
        <AlertTitle>Enhanced AI Processing</AlertTitle>
        <AlertDescription>
          This upload form uses specialized AI models:
          <ul className="mt-2 space-y-1 list-disc list-inside">
            <li><strong>Claude:</strong> Advanced text extraction and understanding from technical documents</li>
            <li><strong>YOLO:</strong> Visual element detection for identifying roof components, measurements, and annotations</li>
          </ul>
        </AlertDescription>
      </Alert>

      <SchematicUploadForm />

      <div className="mt-8 space-y-4">
        <h2 className="text-xl font-semibold">Supported Document Types</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-2">Architectural Blueprints</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Roof framing plans</li>
              <li>• Elevation drawings</li>
              <li>• Construction details</li>
              <li>• Section views</li>
            </ul>
          </div>
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium mb-2">Technical Schematics</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Roofing system diagrams</li>
              <li>• Drainage layouts</li>
              <li>• Material specifications</li>
              <li>• Dimensional drawings</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium mb-2">What Our AI Extracts</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <div>
            <p className="font-medium text-gray-700">Measurements</p>
            <p className="text-gray-600">Roof dimensions, slopes, areas</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Components</p>
            <p className="text-gray-600">Shingles, flashing, vents, gutters</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">Specifications</p>
            <p className="text-gray-600">Materials, grades, installation notes</p>
          </div>
        </div>
      </div>
    </div>
  );
}