import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

const setup = () => {
  const qc = new QueryClient()
  return render(
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('App smoke', () => {
  beforeEach(() => {
    // ensure logged out by default
    localStorage.clear()
  })

  it('renders login redirect when unauthenticated', async () => {
    setup()
    await waitFor(() => {
      expect(document.body.textContent).toContain('登录')
    })
  })
})
