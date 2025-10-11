'use client'

import { use } from 'react'
import TicketDetail from '@/components/TicketDetail'

interface TicketPageProps {
  params: Promise<{
    id: string
  }>
}

export default function TicketPage({ params }: TicketPageProps) {
  const { id } = use(params)
  
  return (
    <div className="min-h-screen bg-gray-50">
      <TicketDetail ticketId={id} />
    </div>
  )
}
