"use client"

import { UnifiedUpload } from "@/components/shared/unified-upload"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Building2, Brain, Eye, Zap, Calculator, CheckCircle, FileCode, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function UploadPage() {
  const features = [
    {
      icon: Building2,
      title: "Scale Detection",
      description: "Automatically detects blueprint scale references and converts measurements to real-world dimensions"
    },
    {
      icon: Eye,
      title: "Computer Vision",
      description: "Uses advanced computer vision to identify roof boundaries, edges, and geometric features"
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Claude AI analyzes document content to extract materials, specifications, and requirements"
    },
    {
      icon: Zap,
      title: "Feature Detection",
      description: "Identifies roof features like exhaust ports, walkways, equipment, and penetrations"
    },
    {
      icon: Calculator,
      title: "Cost Estimation",
      description: "Generates accurate cost estimates based on verified measurements and detected features"
    },
    {
      icon: CheckCircle,
      title: "Verification",
      description: "Cross-validates measurements between OCR and blueprint analysis for maximum accuracy"
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary rounded-xl shadow-sm">
              <Building2 className="h-7 w-7 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-2xl text-slate-900">PDF Pipeline Upload</h1>
              <p className="text-base text-slate-600">Advanced hybrid processing for roofing documents</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Main Upload Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Upload Component */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Upload Document</CardTitle>
                  <CardDescription>
                    Upload PDFs for comprehensive AI-powered processing
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <UnifiedUpload 
                    showPipelineStages={true}
                    redirectToEstimate={true}
                    redirectToProcessing={false}
                  />
                </CardContent>
              </Card>
            </div>

            {/* Features Panel */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Pipeline Features</CardTitle>
                  <CardDescription>
                    Advanced hybrid processing capabilities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <feature.icon className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-medium text-sm">{feature.title}</h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Processing Stages</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-sm">Document Upload & Validation</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm">Document Type Analysis</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm">Hybrid Content Extraction</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <span className="text-sm">Roof Measurement & Features</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-sm">AI Interpretation</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                    <span className="text-sm">Estimate Generation</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Supported Documents</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">Blueprints</Badge>
                    <Badge variant="outline">Specifications</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">Site Plans</Badge>
                    <Badge variant="outline">Material Lists</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">Inspection Reports</Badge>
                    <Badge variant="outline">CAD Drawings</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Schematic Upload Link */}
          <Card className="border-2 border-primary/20 bg-primary/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary rounded-xl">
                    <FileCode className="h-6 w-6 text-primary-foreground" />
                  </div>
                  <div>
                    <CardTitle>Advanced Schematic & Blueprint Analysis</CardTitle>
                    <CardDescription>
                      Specialized AI processing with Qwen and YOLO models
                    </CardDescription>
                  </div>
                </div>
                <Link href="/schematic-upload">
                  <Button variant="default" size="sm">
                    Try Schematic Upload
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                <div className="flex items-start gap-3">
                  <Badge className="mt-0.5" variant="secondary">Qwen</Badge>
                  <div>
                    <h4 className="font-medium text-sm">Advanced Text Extraction</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Extracts technical specifications, measurements, and annotations from complex drawings
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-0.5" variant="secondary">YOLO</Badge>
                  <div>
                    <h4 className="font-medium text-sm">Visual Element Detection</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Identifies roof components, dimension lines, and architectural features
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Badge className="mt-0.5" variant="secondary">AI</Badge>
                  <div>
                    <h4 className="font-medium text-sm">Intelligent Analysis</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Combines text and visual data for comprehensive roofing estimates
                    </p>
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Perfect for architectural blueprints, technical schematics, CAD exports, and detailed construction drawings
              </p>
            </CardContent>
          </Card>

          {/* Benefits Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Why Use Our Hybrid Pipeline?</CardTitle>
              <CardDescription>
                Advanced processing that combines the best of computer vision and AI
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="text-center p-4">
                  <div className="p-3 bg-primary/10 rounded-full w-fit mx-auto mb-3">
                    <CheckCircle className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">98.5% Accuracy</h3>
                  <p className="text-sm text-muted-foreground">
                    Hybrid approach ensures maximum accuracy in measurements and feature detection
                  </p>
                </div>
                <div className="text-center p-4">
                  <div className="p-3 bg-blue-100 rounded-full w-fit mx-auto mb-3">
                    <Zap className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Real-time Processing</h3>
                  <p className="text-sm text-muted-foreground">
                    Live status updates and progress tracking throughout the entire pipeline
                  </p>
                </div>
                <div className="text-center p-4">
                  <div className="p-3 bg-green-100 rounded-full w-fit mx-auto mb-3">
                    <Building2 className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Feature Detection</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatically identifies exhaust ports, walkways, equipment, and other roof features
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
