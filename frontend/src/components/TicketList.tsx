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
import { TicketListResponse, TicketFilters, TicketCreate } from '@/types'
import { apiClient } from '@/lib/api'
import { Dialog, DialogHeader, DialogBody, DialogFooter, Textarea } from '@material-tailwind/react'

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
  const [openCreate, setOpenCreate] = useState(false)
  const [creating, setCreating] = useState(false)
  const [createForm, setCreateForm] = useState<TicketCreate>({
    created_at: new Date().toISOString(),
    customer_name: '',
    channel: 'email',
    subject: '',
    description: '',
    status: 'open',
    priority: 'medium',
  })

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
      if (!response.ok) {
        setTickets([])
        return
      }
      const data = await response.json()
      const items = Array.isArray(data?.items) ? data.items : []
      setTickets(items)
    } catch (error) {
      console.error('Error fetching tickets:', error)
      setTickets([])
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
        <div className="flex items-center gap-4 mb-4">
          <Link href="/">
            <Button
              color="gray"
              variant="text"
              size="sm"
            >
              ← Voltar
            </Button>
          </Link>
          <Typography variant="h2" color="gray">
            Tickets
          </Typography>
          <Button color="blue" size="sm" className="ml-auto" onClick={() => setOpenCreate(true)}>
            Criar Ticket
          </Button>
        </div>
        
        {/* Legenda */}
        <div className="flex items-center gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
          <Typography variant="small" color="gray" className="font-semibold">
            Fonte dos dados:
          </Typography>
          <div className="flex items-center gap-2">
            <Chip color="blue" value="SQLite" size="sm" variant="ghost" />
            <Typography variant="small" color="gray">
              Dados seed (20 primeiros)
            </Typography>
          </div>
          <div className="flex items-center gap-2">
            <Chip color="green" value="CSV" size="sm" variant="ghost" />
            <Typography variant="small" color="gray">
              Importados do CSV externo
            </Typography>
          </div>
        </div>

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
      ) : tickets.length === 0 ? (
        <Card className="bg-orange-50 border border-orange-200">
          <CardBody className="p-5">
            <Typography variant="h5" color="orange" className="mb-1 font-semibold">
              Nenhum ticket encontrado
            </Typography>
            <Typography color="gray">
              Consulte a documentação (README) do projeto para passos de inicialização.
            </Typography>
          </CardBody>
        </Card>
      ) : (
        <div className="grid gap-4">
          {tickets.map((ticket) => (
            <Card key={ticket.id} className="hover:shadow-lg transition-shadow">
              <CardBody>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Typography variant="h5" color="blue-gray">
                        {ticket.subject}
                      </Typography>
                      <Chip
                        color={"blue"}
                        value={"SQLite"}
                        size="sm"
                        variant="ghost"
                      />
                    </div>
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
                    <Button 
                      size="sm" 
                      color="gray" 
                      variant="outlined"
                    >
                      Ver Detalhes
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={openCreate} handler={() => setOpenCreate(false)} size="md">
        <DialogHeader>Criar Ticket</DialogHeader>
        <DialogBody className="space-y-4">
          <Input
            label="Cliente"
            value={createForm.customer_name}
            onChange={(e) => setCreateForm({ ...createForm, customer_name: e.target.value })}
          />
          <Input
            label="Assunto"
            value={createForm.subject}
            onChange={(e) => setCreateForm({ ...createForm, subject: e.target.value })}
          />
          <Textarea
            label="Descrição"
            value={createForm.description || ''}
            onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select label="Status" value={createForm.status} onChange={(val) => setCreateForm({ ...createForm, status: (val || 'open') as any })}>
              <Option value="open">Aberto</Option>
              <Option value="in_progress">Em Progresso</Option>
              <Option value="on_hold">Em Espera</Option>
              <Option value="resolved">Resolvido</Option>
              <Option value="closed">Fechado</Option>
            </Select>
            <Select label="Prioridade" value={createForm.priority} onChange={(val) => setCreateForm({ ...createForm, priority: (val || 'medium') as any })}>
              <Option value="low">Baixa</Option>
              <Option value="medium">Média</Option>
              <Option value="high">Alta</Option>
              <Option value="urgent">Urgente</Option>
            </Select>
            <Select label="Canal" value={createForm.channel} onChange={(val) => setCreateForm({ ...createForm, channel: (val || 'email') as any })}>
              <Option value="email">Email</Option>
              <Option value="slack">Slack</Option>
              <Option value="whatsapp">WhatsApp</Option>
              <Option value="web">Web</Option>
              <Option value="phone">Telefone</Option>
            </Select>
          </div>
        </DialogBody>
        <DialogFooter className="gap-2">
          <Button variant="text" color="gray" onClick={() => setOpenCreate(false)} disabled={creating}>
            Cancelar
          </Button>
          <Button color="blue" disabled={creating || !createForm.customer_name || !createForm.subject}
            onClick={async () => {
              try {
                setCreating(true)
                const payload: TicketCreate = {
                  customer_name: createForm.customer_name,
                  channel: createForm.channel,
                  subject: createForm.subject,
                  description: createForm.description,
                  status: createForm.status,
                  priority: createForm.priority,
                  created_at: new Date().toISOString(),
                }
                await apiClient.createTicket(payload)
                setOpenCreate(false)
                setCreateForm({
                  created_at: new Date().toISOString(),
                  customer_name: '',
                  channel: 'email',
                  subject: '',
                  description: '',
                  status: 'open',
                  priority: 'medium',
                })
                fetchTickets()
              } catch (e) {
                console.error(e)
              } finally {
                setCreating(false)
              }
            }}
          >
            {creating ? 'Criando...' : 'Criar'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  )
}
