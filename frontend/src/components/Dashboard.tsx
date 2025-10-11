'use client'

import { useState, useEffect } from 'react'
import { 
  Card, 
  CardBody, 
  Typography, 
  Spinner,
  Alert
} from '@material-tailwind/react'
import { Metrics } from '@/types'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics')
      if (!response.ok) {
        throw new Error('Erro ao carregar métricas')
      }
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      setError('Erro ao carregar métricas')
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
        <Alert color="red">{error || 'Erro ao carregar métricas'}</Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Typography variant="h2" color="gray" className="mb-8">
        Dashboard
      </Typography>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
              Tempo Médio
            </Typography>
            <Typography variant="h3" color="gray">
              {metrics.avg_resolution_time_hours 
                ? `${metrics.avg_resolution_time_hours}h`
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
      </div>
    </div>
  )
}
