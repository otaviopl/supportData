export interface Ticket {
  id: number
  created_at: string
  updated_at: string
  customer_name: string
  channel: 'email' | 'slack' | 'whatsapp' | 'web' | 'phone'
  subject: string
  description?: string
  status: 'open' | 'in_progress' | 'on_hold' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
}

export interface TicketListResponse {
  items: Ticket[]
  page: number
  page_size: number
  total: number
}

export interface TicketUpdate {
  status?: Ticket['status']
  priority?: Ticket['priority']
}

export interface TicketUpdateResponse {
  id: number
  status: Ticket['status']
  priority: Ticket['priority']
  updated_at: string
}

export interface Metrics {
  tickets_by_day: Array<{ date: string; count: number }>
  status_counts: Record<string, number>
  channel_counts: Record<string, number>
  priority_counts: Record<string, number>
  type_counts: Record<string, number>
  top_products: Array<{ product: string; count: number }>
  total_tickets: number
}

export interface TicketFilters {
  page?: number
  page_size?: number
  q?: string
  status?: Ticket['status']
  priority?: Ticket['priority']
  channel?: Ticket['channel']
}
