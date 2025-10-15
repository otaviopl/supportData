'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Card, 
  CardBody, 
  Typography, 
  Spinner,
  Alert,
  Button,
  Chip,
  IconButton,
  Tooltip
} from '@material-tailwind/react'
import { 
  ExclamationTriangleIcon,
  CommandLineIcon,
  ServerIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'
import { Metrics } from '@/types'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics')
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Erro ao carregar métricas')
      }
      
      setMetrics(data)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar métricas'
      setError(errorMessage)
      console.error('Error fetching metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <Spinner className="h-8 w-8" />
        </div>
      </div>
    )
  }

  if (error || !metrics) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button color="gray" variant="text" size="sm" className="flex items-center gap-2">
              <ArrowLeftIcon className="h-4 w-4" />
              Voltar
            </Button>
          </Link>
          <Typography variant="h2" color="gray">Dashboard</Typography>
        </div>
        <Card className="bg-orange-50 border border-orange-200">
          <CardBody className="p-5">
            <div className="flex items-start gap-3">
              <ExclamationTriangleIcon className="h-6 w-6 text-orange-500" />
              <div>
                <Typography variant="h5" color="orange" className="mb-1 font-semibold">
                  Não foi possível carregar as métricas
                </Typography>
                <Typography color="gray" className="mb-3">
                  Consulte a documentação (README) do projeto para passos de inicialização.
                </Typography>
                <Button color="gray" variant="text" size="sm" onClick={() => window.location.reload()}>
                  Tentar novamente
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-8">
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
          Dashboard
        </Typography>
      </div>

      <div className="flex items-center gap-4 mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <Chip
          color="green"
          value="CSV"
          size="sm"
          variant="filled"
        />
        <div>
          <Typography variant="h6" color="green" className="font-semibold">
            Dados Importados do CSV
          </Typography>
          <Typography variant="small" color="green" className="opacity-80">
            Métricas geradas a partir do arquivo tickets.csv com {metrics?.total_tickets.toLocaleString()} registros
          </Typography>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardBody>
            <Typography variant="h6" color="blue-gray" className="mb-2">
              Total de Tickets
            </Typography>
            <Typography variant="h3" color="gray">
              {metrics.total_tickets.toLocaleString()}
            </Typography>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Typography variant="h6" color="blue-gray" className="mb-2">
              Taxa de Resolução
            </Typography>
            <Typography variant="h3" color="gray">
              {metrics.resolution_rate}%
            </Typography>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Typography variant="h6" color="blue-gray" className="mb-2">
              Tempo Médio Resolução
            </Typography>
            <Typography variant="h3" color="gray">
              {metrics.avg_resolution_time_hours 
                ? `${metrics.avg_resolution_time_hours}h`
                : 'N/A'
              }
            </Typography>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Typography variant="h6" color="blue-gray" className="mb-2">
              Satisfação Média
            </Typography>
            <Typography variant="h3" color="gray">
              {metrics.avg_satisfaction_rating 
                ? `${metrics.avg_satisfaction_rating}/5`
                : 'N/A'
              }
            </Typography>
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status */}
        <Card>
          <CardBody>
            <Typography variant="h4" color="blue-gray" className="mb-4">
              Distribuição por Status
            </Typography>
            <div className="space-y-3">
              {Object.entries(metrics.status_counts).map(([status, count]) => (
                <div key={status} className="flex justify-between items-center">
                  <Typography color="blue-gray" className="capitalize">
                    {status.replace('_', ' ')}
                  </Typography>
                  <Typography color="gray" className="font-semibold">
                    {count.toLocaleString()}
                  </Typography>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Canais */}
        <Card>
          <CardBody>
            <Typography variant="h4" color="blue-gray" className="mb-4">
              Distribuição por Canal
            </Typography>
            <div className="space-y-3">
              {Object.entries(metrics.channel_counts).map(([channel, count]) => (
                <div key={channel} className="flex justify-between items-center">
                  <Typography color="blue-gray" className="capitalize">
                    {channel.replace('_', ' ')}
                  </Typography>
                  <Typography color="gray" className="font-semibold">
                    {count.toLocaleString()}
                  </Typography>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Prioridades */}
        <Card>
          <CardBody>
            <Typography variant="h4" color="blue-gray" className="mb-4">
              Distribuição por Prioridade
            </Typography>
            <div className="space-y-3">
              {Object.entries(metrics.priority_counts).map(([priority, count]) => (
                <div key={priority} className="flex justify-between items-center">
                  <Typography color="blue-gray" className="capitalize">
                    {priority}
                  </Typography>
                  <Typography color="gray" className="font-semibold">
                    {count.toLocaleString()}
                  </Typography>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Top Produtos */}
        <Card>
          <CardBody>
            <Typography variant="h4" color="blue-gray" className="mb-4">
              Top Produtos
            </Typography>
            <div className="space-y-3">
              {metrics.top_products.slice(0, 5).map((product, index) => (
                <div key={product.product} className="flex justify-between items-center">
                  <Typography color="blue-gray">
                    {index + 1}. {product.product}
                  </Typography>
                  <Typography color="gray" className="font-semibold">
                    {product.count}
                  </Typography>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Tipo de Ticket */}
        {metrics.type_counts && Object.keys(metrics.type_counts).length > 0 && (
          <Card>
            <CardBody>
              <Typography variant="h4" color="blue-gray" className="mb-4">
                Distribuição por Tipo
              </Typography>
              <div className="space-y-3">
                {Object.entries(metrics.type_counts).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <Typography color="blue-gray" className="capitalize">
                      {type.replace('_', ' ')}
                    </Typography>
                    <Typography color="gray" className="font-semibold">
                      {count.toLocaleString()}
                    </Typography>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Distribuição por Gênero */}
        {metrics.gender_distribution && Object.keys(metrics.gender_distribution).length > 0 && (
          <Card>
            <CardBody>
              <Typography variant="h4" color="blue-gray" className="mb-4">
                Distribuição por Gênero
              </Typography>
              <div className="space-y-3">
                {Object.entries(metrics.gender_distribution).map(([gender, count]) => (
                  <div key={gender} className="flex justify-between items-center">
                    <Typography color="blue-gray" className="capitalize">
                      {gender === 'male' ? 'Masculino' : gender === 'female' ? 'Feminino' : gender}
                    </Typography>
                    <Typography color="gray" className="font-semibold">
                      {count.toLocaleString()}
                    </Typography>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Tickets ao longo do tempo */}
      {metrics.tickets_by_day && metrics.tickets_by_day.length > 0 && (
        <Card className="mt-6">
          <CardBody>
            <Typography variant="h4" color="blue-gray" className="mb-4">
              Tickets ao Longo do Tempo
            </Typography>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <Typography variant="small" color="gray">
                  Primeiro ticket: {metrics.tickets_by_day[0].date}
                </Typography>
                <Typography variant="small" color="gray">
                  Último ticket: {metrics.tickets_by_day[metrics.tickets_by_day.length - 1].date}
                </Typography>
              </div>
              <div className="flex justify-between text-sm">
                <Typography variant="small" color="gray">
                  Dia com mais tickets: {
                    (() => {
                      const max = metrics.tickets_by_day.reduce((prev, curr) => 
                        curr.count > prev.count ? curr : prev
                      )
                      return `${max.date} (${max.count} tickets)`
                    })()
                  }
                </Typography>
                <Typography variant="small" color="gray">
                  Média diária: {
                    (metrics.total_tickets / metrics.tickets_by_day.length).toFixed(1)
                  } tickets/dia
                </Typography>
              </div>
              <div className="mt-4 h-32 flex items-end gap-1">
                {metrics.tickets_by_day
                  .filter((_, i) => i % Math.ceil(metrics.tickets_by_day.length / 100) === 0)
                  .map((day, index) => {
                    const maxCount = Math.max(...metrics.tickets_by_day.map(d => d.count))
                    const height = (day.count / maxCount) * 100
                    return (
                      <div
                        key={index}
                        className="flex-1 bg-gray-800 hover:bg-gray-600 transition-colors rounded-t"
                        style={{ height: `${height}%`, minHeight: '2px' }}
                        title={`${day.date}: ${day.count} tickets`}
                      />
                    )
                  })
                }
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
