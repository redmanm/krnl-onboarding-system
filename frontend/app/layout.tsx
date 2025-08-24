import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Toaster } from 'sonner'
import { NotificationProvider } from '@/lib/notifications'
import { LoadingProvider } from '@/lib/loading'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

export const metadata: Metadata = {
  title: 'KRNL Onboarding System - Dashboard',
  description: 'Modern multi-agent employee onboarding system built with KRNL technology',
  keywords: ['onboarding', 'HR', 'automation', 'KRNL', 'employee management'],
  authors: [{ name: 'KRNL Labs' }],
  creator: 'KRNL Labs',
  generator: 'Next.js',
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow', // Adjust for production
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body className={`${GeistSans.variable} ${GeistMono.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <LoadingProvider>
            <NotificationProvider>
              {children}
              <Toaster 
                position="top-right"
                expand={false}
                richColors
                closeButton
                theme="dark"
              />
            </NotificationProvider>
          </LoadingProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
