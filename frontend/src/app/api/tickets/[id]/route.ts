import { NextRequest, NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const data = await apiClient.getTicket(id)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching ticket:', error)
    return NextResponse.json(
      { error: 'Failed to fetch ticket' },
      { status: 500 }
    )
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const body = await request.json()
    const data = await apiClient.updateTicket(id, body)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error updating ticket:', error)
    return NextResponse.json(
      { error: 'Failed to update ticket' },
      { status: 500 }
    )
  }
}
