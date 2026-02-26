import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import NotesList from '../components/NotesList'

const mockNotes = [
  { id: 1, title: 'First Note', content: 'Hello world' },
  { id: 2, title: 'Second Note', content: 'Another note' },
]

beforeEach(() => {
  vi.resetAllMocks()
  global.fetch = vi.fn()
})

describe('NotesList', () => {
  it('renders a list of notes fetched from the API', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockNotes,
    })

    render(<NotesList />)

    await waitFor(() => {
      expect(screen.getByText('First Note')).toBeInTheDocument()
      expect(screen.getByText('Second Note')).toBeInTheDocument()
    })
  })

  it('renders an empty state message when there are no notes', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    })

    render(<NotesList />)

    await waitFor(() => {
      expect(screen.getByText(/no notes/i)).toBeInTheDocument()
    })
  })

  it('shows a delete button for each note and calls DELETE on click', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockNotes })
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, json: async () => [mockNotes[1]] })

    render(<NotesList />)

    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
    })

    await userEvent.click(screen.getAllByRole('button', { name: /delete/i })[0])

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/notes/1',
        expect.objectContaining({ method: 'DELETE' })
      )
    })
  })

  it('shows an edit form when the edit button is clicked', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockNotes,
    })

    render(<NotesList />)

    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /edit/i })).toHaveLength(2)
    })

    await userEvent.click(screen.getAllByRole('button', { name: /edit/i })[0])

    expect(screen.getByDisplayValue('First Note')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Hello world')).toBeInTheDocument()
  })

  it('calls PUT when the edit form is submitted', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockNotes })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, title: 'Updated', content: 'Hello world' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { id: 1, title: 'Updated', content: 'Hello world' },
          mockNotes[1],
        ],
      })

    render(<NotesList />)

    await waitFor(() => screen.getAllByRole('button', { name: /edit/i }))
    await userEvent.click(screen.getAllByRole('button', { name: /edit/i })[0])

    const titleInput = screen.getByDisplayValue('First Note')
    await userEvent.clear(titleInput)
    await userEvent.type(titleInput, 'Updated')

    await userEvent.click(screen.getByRole('button', { name: /save/i }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/notes/1',
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })
})
