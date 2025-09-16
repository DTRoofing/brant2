import { type NextRequest, NextResponse } from "next/server"
import { dbUtils, prisma } from "@/lib/database"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const customerId = searchParams.get("customerId")

    let estimates

    if (customerId) {
      estimates = await dbUtils.getEstimatesByCustomer(customerId)
    } else {
      // Get all estimates/projects
      estimates = await prisma.estimate.findMany({
        include: {
          customer: true,
          measurements: true,
          lineItems: true,
          documents: true,
        },
        orderBy: { createdAt: "desc" },
      })
    }

    console.log("[v0] Fetching projects/estimates for customer:", customerId)

    return NextResponse.json({
      success: true,
      data: estimates,
    })
  } catch (error) {
    console.error("[v0] Error fetching projects:", error)
    return NextResponse.json({ success: false, error: "Failed to fetch projects" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { customerName, customerEmail, customerPhone, customerAddress, projectAddress } = body

    const customer = await dbUtils.createCustomer({
      name: customerName,
      email: customerEmail,
      phone: customerPhone,
      address: customerAddress,
      projectAddress,
    })

    const newEstimate = await dbUtils.createEstimate({
      customerId: customer.id,
      projectAddress,
      status: "DRAFT",
    })

    console.log("[v0] Created new project/estimate:", newEstimate.id)

    return NextResponse.json({
      success: true,
      data: newEstimate,
    })
  } catch (error) {
    console.error("[v0] Error creating project:", error)
    return NextResponse.json({ success: false, error: "Failed to create project" }, { status: 500 })
  }
}
