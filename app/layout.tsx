import React from "react"
import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'

import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains-mono' })

export const metadata: Metadata = {
  title: 'FinSight AI - Indian Stock Market Analytics',
  description: 'Real-time Indian stock market analytics dashboard tracking 50 NSE/BSE companies with conversational AI, NLP-powered sentiment analysis, and market trend insights using the OpenDialog framework.',
}

export const viewport: Viewport = {
  themeColor: '#0a1128',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>{children}</body>
    </html>
  )
}
