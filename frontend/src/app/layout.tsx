import type { Metadata } from 'next'
import { MaterialTailwindProvider } from '@/lib/material-tailwind'
import './globals.css'

export const metadata: Metadata = {
  title: 'Support Tickets',
  description: 'Sistema de gerenciamento de tickets de suporte',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>
        <MaterialTailwindProvider>
          {children}
        </MaterialTailwindProvider>
      </body>
    </html>
  )
}
