'use client'

import Link from 'next/link'
import { Button } from '@material-tailwind/react'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Support Tickets
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            Sistema de gerenciamento de tickets de suporte
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link href="/tickets">
              <Button 
                color="gray" 
                size="lg" 
                className="bg-gray-900"
              >
                Ver Tickets
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button 
                color="gray" 
                variant="outlined" 
                size="lg"
              >
                Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
