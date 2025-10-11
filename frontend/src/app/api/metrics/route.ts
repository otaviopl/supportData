import { NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

export async function GET() {
  try {
    const data = await apiClient.getMetrics()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching metrics:', error)
    return NextResponse.json(
      { error: 'Failed to fetch metrics' },
      { status: 500 }
    )
  }
}
