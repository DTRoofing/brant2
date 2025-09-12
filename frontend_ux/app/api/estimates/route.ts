import { type NextRequest, NextResponse } from "next/server"
import { dbUtils } from "@/lib/database"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const customerId = searchParams.get("customerId")

    let estimates

    if (customerId) {
      estimates = await dbUtils.getEstimatesByCustomer(customerId)
    } else {
      // Get all estimates if no customer specified
      estimates = await dbUtils.prisma.estimate.findMany({
        include: {
          customer: true,
          measurements: true,
          lineItems: true,
          documents: true,
        },
        orderBy: { createdAt: "desc" },
      })
    }

    return NextResponse.json({
      success: true,
      data: estimates,
    })
  } catch (error) {
    console.error("[v0] Error fetching estimates:", error)
    return NextResponse.json({ success: false, error: "Failed to fetch estimates" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { customerId, totalCost, confidence, summary, pdfUrl, projectAddress, measurements, lineItems, documents } =
      body

    const newEstimate = await dbUtils.createEstimateWithDetails({
      customer: {
        name: body.customerName || "Unknown Customer",
        email: body.customerEmail,
        phone: body.customerPhone,
        address: body.customerAddress,
        projectAddress,
      },
      estimate: {
        totalCost: totalCost ? Number.parseFloat(totalCost) : undefined,
        confidence: confidence || 0,
        summary,
        pdfUrl,
        projectAddress,
      },
      measurements: measurements || [],
      lineItems: lineItems || [],
      documents: documents || [],
    })

    console.log("[v0] Created new estimate with Prisma:", newEstimate.id)

    return NextResponse.json({
      success: true,
      data: newEstimate,
    })
  } catch (error) {
    console.error("[v0] Error creating estimate:", error)
    return NextResponse.json({ success: false, error: "Failed to create estimate" }, { status: 500 })
  }
}
