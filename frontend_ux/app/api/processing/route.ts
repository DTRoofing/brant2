import { type NextRequest, NextResponse } from "next/server"
import { DocumentProcessorServiceClient } from "@google-cloud/documentai"
import { ImageAnnotatorClient } from "@google-cloud/vision"
import { Storage } from "@google-cloud/storage"
import { dbUtils, prisma } from "@/lib/database"
import Anthropic from "@anthropic-ai/sdk"

// Initialize Google Cloud clients
const documentAIClient = new DocumentProcessorServiceClient({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
})

const visionClient = new ImageAnnotatorClient({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
})

const storage = new Storage({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
})

const claude = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { estimateId, documentId, processingType } = body

    console.log("[v0] Starting Google Cloud AI processing:", { estimateId, documentId, processingType })

    const document = await prisma.document.findUnique({
      where: { id: documentId },
      include: { estimate: true },
    })

    if (!document) {
      return NextResponse.json({ success: false, error: "Document not found" }, { status: 404 })
    }

    // Create audit trail entry
    await dbUtils.createAuditEntry({
      estimateId: document.estimateId,
      action: "AI_PROCESSING_STARTED",
      details: `Started ${processingType} processing for document ${document.fileName}`,
      source: "SYSTEM",
      confidence: 1.0,
    })

    // Start AI processing (async)
    processDocumentWithAI(document.id, document.fileUrl, processingType, document.estimateId)

    return NextResponse.json({
      success: true,
      message: "Google Cloud AI processing started",
      documentId,
      processingType,
    })
  } catch (error) {
    console.error("[v0] Error starting Google Cloud AI processing:", error)
    return NextResponse.json({ success: false, error: "Failed to start AI processing" }, { status: 500 })
  }
}

async function processDocumentWithAI(documentId: string, filePath: string, processingType: string, estimateId: string) {
  try {
    await dbUtils.updateEstimate(estimateId, { status: "PROCESSING" })

    if (processingType === "claude_expert" && process.env.ANTHROPIC_API_KEY) {
      console.log("[v0] Processing document with Claude AI roofing expert...")

      // Get file from Google Cloud Storage
      const bucket = storage.bucket(process.env.GOOGLE_CLOUD_STORAGE_BUCKET!)
      const file = bucket.file(filePath)
      const [fileBuffer] = await file.download()

      // Convert PDF to base64 for Claude
      const base64Content = fileBuffer.toString("base64")

      const claudePrompt = `Act as an engineer and commercial roofing expert. Create a complete and comprehensive roofing estimate based on the provided PDF document. 

Include all the line items like:
- Materials (membrane, insulation, fasteners, adhesives, flashing, drains, etc.)
- Labor (installation, removal, preparation, cleanup)
- Permits (building permits, safety permits)
- Edge cases (weather delays, access issues, structural repairs)
- Equipment rental
- Safety requirements
- Overhead and profit

Provide a detailed summary and itemized breakdown. For each line item, include:
- Description
- Quantity
- Unit of measure
- Unit cost (if determinable from document)
- Total cost
- Notes about source in document

Format the response as JSON with this structure:
{
  "summary": {
    "projectType": "string",
    "totalSquareFootage": "number or null if not determinable",
    "roofType": "string",
    "estimatedTotal": "number or null",
    "confidence": "number between 0-1"
  },
  "lineItems": [
    {
      "category": "MATERIAL|LABOR|PERMIT|EQUIPMENT|SAFETY|OTHER",
      "description": "string",
      "quantity": "number or null",
      "unit": "string",
      "unitCost": "number or null",
      "totalCost": "number or null",
      "notes": "string",
      "confidence": "number between 0-1",
      "sourceReference": "page number or section where found"
    }
  ],
  "measurements": [
    {
      "area": "string description",
      "squareFeet": "number or null",
      "confidence": "number between 0-1",
      "sourceReference": "where this measurement was found"
    }
  ]
}`

      const response = await claude.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 4000,
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: claudePrompt,
              },
              {
                type: "image",
                source: {
                  type: "base64",
                  media_type: "application/pdf",
                  data: base64Content,
                },
              },
            ],
          },
        ],
      })

      const claudeResult = JSON.parse(response.content[0].text)

      const aiResults = {
        claudeExpert: {
          confidence: claudeResult.summary.confidence || 0.8,
          summary: claudeResult.summary,
          lineItems: claudeResult.lineItems || [],
          measurements: claudeResult.measurements || [],
          rawResponse: response.content[0].text,
        },
      }

      // Create measurements from Claude results
      for (const measurement of claudeResult.measurements || []) {
        if (measurement.squareFeet && measurement.squareFeet > 0) {
          await dbUtils.createMeasurement({
            estimateId,
            area: measurement.area,
            squareFeet: measurement.squareFeet,
            confidence: measurement.confidence || 0.8,
            source: "claude_expert_extracted",
            notes: `Claude AI Expert Analysis - ${measurement.sourceReference || "Source not specified"}`,
          })
        }
      }

      // Create line items from Claude results
      for (const lineItem of claudeResult.lineItems || []) {
        await dbUtils.createLineItem({
          estimateId,
          category: lineItem.category || "OTHER",
          description: lineItem.description,
          quantity: lineItem.quantity || null,
          unit: lineItem.unit || "each",
          unitCost: lineItem.unitCost || null,
          totalCost: lineItem.totalCost || null,
          source: "claude_expert",
          confidence: lineItem.confidence || 0.8,
          notes: `${lineItem.notes || ""} - Source: ${lineItem.sourceReference || "Not specified"}`,
        })
      }

      // Update estimate with Claude results
      await dbUtils.updateEstimate(estimateId, {
        summary: JSON.stringify(aiResults),
        confidence: aiResults.claudeExpert.confidence,
      })

      console.log("[v0] Claude AI expert processing completed successfully")
    } else if (processingType === "document_ai" && process.env.ENABLE_DOCUMENT_AI === "true") {
      const processorName = `projects/${process.env.GOOGLE_CLOUD_PROJECT_ID}/locations/${process.env.DOCUMENT_AI_LOCATION || "us"}/processors/${process.env.DOCUMENT_AI_PROCESSOR_ID}`

      console.log("[v0] Using Document AI processor:", processorName)

      // Get file from Google Cloud Storage
      const bucket = storage.bucket(process.env.GOOGLE_CLOUD_STORAGE_BUCKET!)
      const file = bucket.file(filePath)
      const [fileBuffer] = await file.download()

      const request = {
        name: processorName,
        rawDocument: {
          content: fileBuffer.toString("base64"),
          mimeType: "application/pdf",
        },
      }

      console.log("[v0] Processing document with Document AI...")
      const [result] = await documentAIClient.processDocument(request)
      const document = result.document

      console.log("[v0] Document AI processing completed, extracting roofing data...")

      const aiResults = {
        documentAI: {
          confidence: document?.pages?.[0]?.pageAnchor?.confidence || 0,
          extractedText: document?.text || "",
          entities: document?.entities || [],
          pages: document?.pages || [],
          roofingData: extractRoofingSpecificData(document),
        },
      }

      // Extract measurements and line items from AI results
      const measurements = extractMeasurements(document, estimateId)
      const lineItems = extractLineItems(document, estimateId)

      console.log("[v0] Extracted measurements:", measurements.length)
      console.log("[v0] Extracted line items:", lineItems.length)

      // Create measurements
      for (const measurement of measurements) {
        await dbUtils.createMeasurement(measurement)
      }

      // Create line items
      for (const lineItem of lineItems) {
        await dbUtils.createLineItem(lineItem)
      }

      // Update estimate with AI results
      await dbUtils.updateEstimate(estimateId, {
        summary: JSON.stringify(aiResults),
        confidence: aiResults.documentAI.confidence,
      })

      console.log("[v0] Document AI processing completed successfully")
    } else if (processingType === "vision_ai") {
      const request = {
        image: { source: { gcsImageUri: `gs://${process.env.GOOGLE_CLOUD_STORAGE_BUCKET}/${filePath}` } },
        features: [{ type: "TEXT_DETECTION" }, { type: "DOCUMENT_TEXT_DETECTION" }, { type: "OBJECT_LOCALIZATION" }],
      }

      const [result] = await visionClient.annotateImage(request)

      const visionResults = {
        visionAI: {
          confidence: result.textAnnotations?.[0]?.confidence || 0,
          textAnnotations: result.textAnnotations || [],
          fullTextAnnotation: result.fullTextAnnotation || null,
          localizedObjectAnnotations: result.localizedObjectAnnotations || [],
        },
      }

      await dbUtils.updateEstimate(estimateId, {
        summary: JSON.stringify(visionResults),
        confidence: visionResults.visionAI.confidence,
      })
    }

    await dbUtils.updateEstimate(estimateId, { status: "COMPLETED" })

    await dbUtils.createAuditEntry({
      estimateId,
      action: "AI_PROCESSING_COMPLETED",
      details: `Completed ${processingType} processing successfully`,
      source: "AI_SYSTEM",
      confidence: 1.0,
    })

    console.log("[v0] Google Cloud AI processing completed for:", documentId)
  } catch (error) {
    console.error("[v0] Google Cloud AI processing failed:", error)

    await dbUtils.updateEstimate(estimateId, { status: "REVIEW" })

    await dbUtils.createAuditEntry({
      estimateId,
      action: "AI_PROCESSING_FAILED",
      details: `Processing failed: ${error.message}`,
      source: "AI_SYSTEM",
      confidence: 0,
    })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const estimateId = searchParams.get("estimateId")

    if (!estimateId) {
      return NextResponse.json({ success: false, error: "Estimate ID required" }, { status: 400 })
    }

    const estimate = await dbUtils.getEstimateById(estimateId)

    if (!estimate) {
      return NextResponse.json({ success: false, error: "Estimate not found" }, { status: 404 })
    }

    console.log("[v0] Fetching processing status for estimate:", estimateId)

    return NextResponse.json({
      success: true,
      data: {
        estimateId,
        status: estimate.status,
        confidence: estimate.confidence,
        summary: estimate.summary ? JSON.parse(estimate.summary) : null,
        measurements: estimate.measurements,
        lineItems: estimate.lineItems,
        auditTrail: estimate.auditTrail,
        overallProgress: calculateOverallProgress(estimate.status),
      },
    })
  } catch (error) {
    console.error("[v0] Error fetching processing status:", error)
    return NextResponse.json({ success: false, error: "Failed to fetch processing status" }, { status: 500 })
  }
}

function calculateOverallProgress(status: string): number {
  switch (status) {
    case "DRAFT":
      return 0
    case "PROCESSING":
      return 50
    case "COMPLETED":
      return 100
    case "REVIEW":
      return 75
    case "APPROVED":
      return 100
    case "REJECTED":
      return 100
    default:
      return 0
  }
}

function extractMeasurements(document: any, estimateId: string) {
  const measurements = []

  if (document?.entities) {
    for (const entity of document.entities) {
      // Only process entities with high confidence and clear area/dimension data
      if ((entity.type === "area" || entity.type === "dimension") && entity.confidence >= 0.7) {
        const squareFeet = Number.parseFloat(entity.normalizedValue?.text || "0")

        if (squareFeet > 0 && entity.mentionText && entity.mentionText.trim() !== "") {
          measurements.push({
            estimateId,
            area: entity.mentionText,
            squareFeet,
            confidence: entity.confidence,
            source: "document_ai_pdf_extracted",
            notes: `Extracted from PDF page ${entity.pageAnchor?.pageRefs?.[0]?.page || 1} - "${entity.mentionText}"`,
          })
        }
      }
    }
  }

  if (document?.text) {
    const text = document.text
    const areaPatterns = [
      /(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sq\.?\s*ft\.?|square\s+feet?|sf)\b/gi,
      /(\d+(?:,\d{3})*(?:\.\d+)?)\s*x\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:ft\.?|feet?)\b/gi,
    ]

    for (const pattern of areaPatterns) {
      let match
      while ((match = pattern.exec(text)) !== null) {
        let squareFeet = 0
        let description = ""

        if (match.length === 2) {
          // Direct square footage match
          squareFeet = Number.parseFloat(match[1].replace(/,/g, ""))
          description = `${match[1]} sq ft`
        } else if (match.length === 3) {
          // Length x Width calculation
          const length = Number.parseFloat(match[1].replace(/,/g, ""))
          const width = Number.parseFloat(match[2].replace(/,/g, ""))
          squareFeet = length * width
          description = `${match[1]} x ${match[2]} ft (calculated)`
        }

        if (squareFeet > 0) {
          measurements.push({
            estimateId,
            area: description,
            squareFeet,
            confidence: 0.8, // High confidence for regex-extracted measurements
            source: "document_ai_text_extracted",
            notes: `Extracted from PDF text: "${match[0]}"`,
          })
        }
      }
    }
  }

  return measurements
}

function extractLineItems(document: any, estimateId: string) {
  const lineItems = []

  // This is a simplified extraction - in reality, you'd use more sophisticated parsing
  if (document?.entities) {
    for (const entity of document.entities) {
      if (entity.type === "material" || entity.type === "cost") {
        lineItems.push({
          estimateId,
          category: "MATERIAL" as const,
          description: entity.mentionText || "Unknown Item",
          quantity: 1,
          unit: "each",
          source: "document_ai",
          confidence: entity.confidence || 0.5,
        })
      }
    }
  }

  return lineItems
}

function extractRoofingSpecificData(document: any) {
  const roofingData = {
    buildingDimensions: [],
    roofType: null,
    materials: [],
    laborRequirements: [],
    permits: [],
    safetyRequirements: [],
  }

  if (document?.text) {
    const text = document.text.toLowerCase()

    // Extract roof type
    if (text.includes("tpo") || text.includes("thermoplastic")) {
      roofingData.roofType = "TPO"
    } else if (text.includes("epdm") || text.includes("rubber")) {
      roofingData.roofType = "EPDM"
    } else if (text.includes("modified bitumen") || text.includes("mod bit")) {
      roofingData.roofType = "Modified Bitumen"
    } else if (text.includes("built-up") || text.includes("bur")) {
      roofingData.roofType = "Built-Up Roof"
    }

    // Extract common roofing materials
    const materialKeywords = ["membrane", "insulation", "fastener", "adhesive", "flashing", "drain", "scupper"]
    materialKeywords.forEach((keyword) => {
      if (text.includes(keyword)) {
        roofingData.materials.push(keyword)
      }
    })
  }

  return roofingData
}
