'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Button, 
  Card, 
  CardBody, 
  Typography, 
  Chip,
  Input,
  Select,
  Option,
  Spinner
} from '@material-tailwind/react'
import { TicketListResponse, TicketFilters } from '@/types'

interface TicketListProps {
  initialData?: TicketListResponse
}

export default function TicketList({ initialData }: TicketListProps) {
  const [tickets, setTickets] = useState(initialData?.items || [])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState<TicketFilters>({
    page: 1,
    page_size: 20,
  })
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [channelFilter, setChannelFilter] = useState('')

  const fetchTickets = async () => {
    setLoading(true)
    try {
      const queryParams = new URLSearchParams()
      queryParams.append('page', filters.page?.toString() || '1')
      queryParams.append('page_size', filters.page_size?.toString() || '20')
      
      if (search) queryParams.append('q', search)
      if (statusFilter) queryParams.append('status', statusFilter)
      if (priorityFilter) queryParams.append('priority', priorityFilter)
      if (channelFilter) queryParams.append('channel', channelFilter)

      const response = await fetch(`/api/tickets?${queryParams}`)
      const data = await response.json()
      setTickets(data.items)
    } catch (error) {
      console.error('Error fetching tickets:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTickets()
  }, [filters, search, statusFilter, priorityFilter, channelFilter])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'blue'
      case 'in_progress': return 'yellow'
      case 'on_hold': return 'orange'
      case 'resolved': return 'green'
      case 'closed': return 'gray'
      default: return 'gray'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'green'
      case 'medium': return 'yellow'
      case 'high': return 'orange'
      case 'urgent': return 'red'
      default: return 'gray'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <Typography variant="h2" color="gray" className="mb-4">
          Tickets
        </Typography>
        
        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Input
            label="Buscar"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por assunto ou cliente..."
          />
          
          <Select
            label="Status"
            value={statusFilter}
            onChange={(val) => setStatusFilter(val || '')}
          >
            <Option value="">Todos</Option>
            <Option value="open">Aberto</Option>
            <Option value="in_progress">Em Progresso</Option>
            <Option value="on_hold">Em Espera</Option>
            <Option value="resolved">Resolvido</Option>
            <Option value="closed">Fechado</Option>
          </Select>
          
          <Select
            label="Prioridade"
            value={priorityFilter}
            onChange={(val) => setPriorityFilter(val || '')}
          >
            <Option value="">Todas</Option>
            <Option value="low">Baixa</Option>
            <Option value="medium">Média</Option>
            <Option value="high">Alta</Option>
            <Option value="urgent">Urgente</Option>
          </Select>
          
          <Select
            label="Canal"
            value={channelFilter}
            onChange={(val) => setChannelFilter(val || '')}
          >
            <Option value="">Todos</Option>
            <Option value="email">Email</Option>
            <Option value="slack">Slack</Option>
            <Option value="whatsapp">WhatsApp</Option>
            <Option value="web">Web</Option>
            <Option value="phone">Telefone</Option>
          </Select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner className="h-8 w-8" />
        </div>
      ) : (
        <div className="grid gap-4">
          {tickets.map((ticket) => (
            <Card key={ticket.id} className="hover:shadow-lg transition-shadow">
              <CardBody>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <Typography variant="h5" color="blue-gray" className="mb-2">
                      {ticket.subject}
                    </Typography>
                    <Typography color="gray" className="mb-2">
                      Cliente: {ticket.customer_name}
                    </Typography>
                    <Typography color="gray" variant="small">
                      {new Date(ticket.created_at).toLocaleDateString('pt-BR')}
                    </Typography>
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Chip
                      color={getStatusColor(ticket.status)}
                      value={ticket.status}
                      size="sm"
                    />
                    <Chip
                      color={getPriorityColor(ticket.priority)}
                      value={ticket.priority}
                      size="sm"
                    />
                    <Chip
                      color="gray"
                      value={ticket.channel}
                      size="sm"
                    />
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <Link href={`/tickets/${ticket.id}`}>
                    <Button size="sm" color="gray" variant="outlined" placeholder="">
                      Ver Detalhes
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
