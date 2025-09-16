import { type NextRequest, NextResponse } from "next/server"
import { dbUtils } from "@/lib/database"

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const estimateId = params.id

    const estimate = await dbUtils.getEstimateById(estimateId)

    if (!estimate) {
      return NextResponse.json({ success: false, error: "Estimate not found" }, { status: 404 })
    }

    console.log("[v0] Fetching estimate:", estimateId)

    return NextResponse.json({
      success: true,
      data: estimate,
    })
  } catch (error) {
    console.error("[v0] Error fetching estimate:", error)
    return NextResponse.json({ success: false, error: "Failed to fetch estimate" }, { status: 500 })
  }
}

export async function PUT(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const estimateId = params.id
    const body = await request.json()

    const updatedEstimate = await dbUtils.updateEstimate(estimateId, body)

    console.log("[v0] Updated estimate:", estimateId)

    return NextResponse.json({
      success: true,
      data: updatedEstimate,
      message: "Estimate updated successfully",
    })
  } catch (error) {
    console.error("[v0] Error updating estimate:", error)
    return NextResponse.json({ success: false, error: "Failed to update estimate" }, { status: 500 })
  }
}
