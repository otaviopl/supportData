'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Button, 
  Card, 
  CardBody, 
  Typography, 
  Chip,
  Select,
  Option,
  Spinner,
  Alert
} from '@material-tailwind/react'
import { Ticket, TicketUpdate } from '@/types'

interface TicketDetailProps {
  ticketId: string
}

export default function TicketDetail({ ticketId }: TicketDetailProps) {
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [form, setForm] = useState<{ status: Ticket['status']; priority: Ticket['priority'] } | null>(null)
  const router = useRouter()

  const fetchTicket = async () => {
    try {
      const response = await fetch(`/api/tickets/${ticketId}`)
      if (!response.ok) {
        throw new Error('Ticket não encontrado')
      }
      const data = await response.json()
      setTicket(data)
      setForm({ status: data.status, priority: data.priority })
    } catch (error) {
      setError('Erro ao carregar ticket')
      console.error('Error fetching ticket:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateTicket = async (update: TicketUpdate) => {
    setUpdating(true)
    setError('')
    setSuccess('')
    
    try {
      const response = await fetch(`/api/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(update),
      })
      
      if (!response.ok) {
        throw new Error('Erro ao atualizar ticket')
      }
      
      const data = await response.json()
      setTicket(prev => prev ? { ...prev, ...data } : null)
      setSuccess('Ticket atualizado com sucesso!')
      setForm({ status: data.status, priority: data.priority })
    } catch (error) {
      setError('Erro ao atualizar ticket')
      console.error('Error updating ticket:', error)
    } finally {
      setUpdating(false)
    }
  }

  const handleSave = async () => {
    if (!ticket || !form) return
    const update: TicketUpdate = {}
    if (form.status !== ticket.status) update.status = form.status
    if (form.priority !== ticket.priority) update.priority = form.priority
    if (Object.keys(update).length === 0) return
    await updateTicket(update)
  }

  const handleCancel = () => {
    if (!ticket) return
    setForm({ status: ticket.status, priority: ticket.priority })
    setSuccess('')
    setError('')
  }

  useEffect(() => {
    fetchTicket()
  }, [ticketId])

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

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <Spinner className="h-8 w-8" />
        </div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert color="red">Ticket não encontrado</Alert>
      </div>
    )
  }

  const isDirty = !!(ticket && form && (form.status !== ticket.status || form.priority !== ticket.priority))

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button
          color="gray"
          variant="text"
          onClick={() => router.back()}
          className="mb-2"
        >
          ← Voltar
        </Button>
      </div>

      {error && (
        <Alert color="red" className="mb-4">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert color="green" className="mb-4">
          {success}
        </Alert>
      )}

      <Card>
        <CardBody>
          <div className="flex items-center gap-3 mb-4">
            <Typography variant="h2" color="gray">
              Ticket #{ticket.id}
            </Typography>
            <Chip
              color={"blue"}
              value={"SQLite"}
              size="sm"
            />
          </div>

          <Typography variant="h4" color="blue-gray" className="mb-4">
            {ticket.subject}
          </Typography>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Typography variant="h6" color="gray">Cliente</Typography>
                <Typography color="blue-gray">{ticket.customer_name}</Typography>
              </div>
              <div>
                <Typography variant="h6" color="gray">Canal</Typography>
                <Chip color="gray" value={ticket.channel} />
              </div>
              <div>
                <Typography variant="h6" color="gray">Descrição</Typography>
                <Typography color="blue-gray">{ticket.description || 'Sem descrição'}</Typography>
              </div>
              <div>
                <Typography variant="h6" color="gray">Datas</Typography>
                <Typography color="blue-gray">Criado: {new Date(ticket.created_at).toLocaleString('pt-BR')}</Typography>
                <Typography color="blue-gray">Atualizado: {new Date(ticket.updated_at).toLocaleString('pt-BR')}</Typography>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <Typography variant="h6" color="gray" className="mb-2">Status</Typography>
                <Select
                  value={form?.status}
                  onChange={(val) => val && setForm(prev => prev ? { ...prev, status: val as any } : prev)}
                  disabled={updating}
                  className="z-50"
                >
                  <Option value="open">Aberto</Option>
                  <Option value="in_progress">Em Progresso</Option>
                  <Option value="on_hold">Em Espera</Option>
                  <Option value="resolved">Resolvido</Option>
                  <Option value="closed">Fechado</Option>
                </Select>
              </div>

              <div>
                <Typography variant="h6" color="gray" className="mb-2">Prioridade</Typography>
                <Select
                  value={form?.priority}
                  onChange={(val) => val && setForm(prev => prev ? { ...prev, priority: val as any } : prev)}
                  disabled={updating}
                  className="z-50"
                >
                  <Option value="low">Baixa</Option>
                  <Option value="medium">Média</Option>
                  <Option value="high">Alta</Option>
                  <Option value="urgent">Urgente</Option>
                </Select>
              </div>

              <div className="pt-2">
                <Typography variant="h6" color="gray" className="mb-2">Status Atual</Typography>
                <div className="flex gap-2">
                  <Chip color={getStatusColor(form?.status || ticket.status)} value={form?.status || ticket.status} />
                  <Chip color={getPriorityColor(form?.priority || ticket.priority)} value={form?.priority || ticket.priority} />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-end gap-2">
            <Button color="gray" variant="text" onClick={handleCancel} disabled={!isDirty || updating}>
              Cancelar
            </Button>
            <Button color="blue" onClick={handleSave} disabled={!isDirty || updating}>
              {updating ? 'Salvando...' : 'Salvar alterações'}
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
