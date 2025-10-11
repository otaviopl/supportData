import { NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

export async function GET() {
  try {
    const data = await apiClient.getMetrics()
    
    // Verificar se as métricas estão vazias
    if (!data || Object.keys(data).length === 0 || data.total_tickets === 0) {
      return NextResponse.json(
        { 
          error: 'Métricas não encontradas ou vazias',
          message: 'Execute: python data/etl_support.py para gerar métricas'
        },
        { status: 404 }
      )
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching metrics:', error)
    
    // Verificar se é erro de conexão
    if (error instanceof Error && error.message.includes('ECONNREFUSED')) {
      return NextResponse.json(
        { 
          error: 'Backend não está rodando',
          message: 'Execute: make run-backend para iniciar o servidor'
        },
        { status: 503 }
      )
    }
    
    return NextResponse.json(
      { 
        error: 'Falha ao buscar métricas',
        message: 'Verifique se o backend está rodando e as métricas foram geradas'
      },
      { status: 500 }
    )
  }
}
