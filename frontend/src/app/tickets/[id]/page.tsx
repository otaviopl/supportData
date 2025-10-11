import TicketDetail from '@/components/TicketDetail'

interface TicketPageProps {
  params: {
    id: string
  }
}

export default function TicketPage({ params }: TicketPageProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <TicketDetail ticketId={params.id} />
    </div>
  )
}
