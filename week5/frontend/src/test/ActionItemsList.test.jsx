import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ActionItemsList from '../components/ActionItemsList'

const mockItems = [
  { id: 1, description: 'Ship it', completed: false },
  { id: 2, description: 'Done already', completed: true },
]

beforeEach(() => {
  vi.resetAllMocks()
  global.fetch = vi.fn()
})

describe('ActionItemsList', () => {
  it('renders a list of action items fetched from the API', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockItems,
    })

    render(<ActionItemsList />)

    await waitFor(() => {
      expect(screen.getByText('Ship it')).toBeInTheDocument()
      expect(screen.getByText('Done already')).toBeInTheDocument()
    })
  })

  it('shows a Complete button only for incomplete items', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockItems,
    })

    render(<ActionItemsList />)

    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /complete/i })).toHaveLength(1)
    })
  })

  it('calls PUT /action-items/{id}/complete when Complete is clicked', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockItems })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, description: 'Ship it', completed: true }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: 1, description: 'Ship it', completed: true },
          mockItems[1],
        ],
      })

    render(<ActionItemsList />)

    await waitFor(() => screen.getByRole('button', { name: /complete/i }))
    await userEvent.click(screen.getByRole('button', { name: /complete/i }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/action-items/1/complete',
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })

  it('renders an empty state message when there are no action items', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    })

    render(<ActionItemsList />)

    await waitFor(() => {
      expect(screen.getByText(/no action items/i)).toBeInTheDocument()
    })
  })
})
