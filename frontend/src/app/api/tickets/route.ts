import { NextRequest, NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    const filters = {
      page: searchParams.get('page') ? parseInt(searchParams.get('page')!) : undefined,
      page_size: searchParams.get('page_size') ? parseInt(searchParams.get('page_size')!) : undefined,
      q: searchParams.get('q') || undefined,
      status: searchParams.get('status') as any || undefined,
      priority: searchParams.get('priority') as any || undefined,
      channel: searchParams.get('channel') as any || undefined,
    }

    const data = await apiClient.getTickets(filters)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching tickets:', error)
    return NextResponse.json(
      { error: 'Failed to fetch tickets' },
      { status: 500 }
    )
  }
}
