import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'

const PAGE_SIZE = 5

const NotesList = forwardRef(function NotesList(_, ref) {
  const [notes, setNotes] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')

  // Search state
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null) // null = not in search mode
  const [page, setPage] = useState(1)

  async function loadNotes() {
    const res = await fetch('/notes/')
    if (!res.ok) return
    setNotes(await res.json())
  }

  async function runSearch(q, p = 1) {
    const params = new URLSearchParams({ q, page: p, page_size: PAGE_SIZE, sort: 'created_desc' })
    const res = await fetch(`/notes/search/?${params}`)
    if (!res.ok) return
    setSearchResults(await res.json())
    setPage(p)
  }

  useEffect(() => {
    loadNotes()
  }, [])

  useImperativeHandle(ref, () => ({
    reload: () => {
      loadNotes()
      if (query) runSearch(query, page)
    },
  }))

  async function handleDelete(id) {
    await fetch(`/notes/${id}`, { method: 'DELETE' })
    loadNotes()
    if (query) runSearch(query, page)
  }

  function startEdit(note) {
    setEditingId(note.id)
    setEditTitle(note.title)
    setEditContent(note.content)
  }

  async function handleSave(id) {
    await fetch(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: editTitle, content: editContent }),
    })
    setEditingId(null)
    loadNotes()
    if (query) runSearch(query, page)
  }

  function handleQueryChange(e) {
    const q = e.target.value
    setQuery(q)
    if (q) {
      runSearch(q, 1)
    } else {
      setSearchResults(null)
      setPage(1)
    }
  }

  const isSearching = searchResults !== null
  const displayNotes = isSearching ? searchResults.items : notes
  const totalPages = isSearching ? Math.ceil(searchResults.total / PAGE_SIZE) : 0

  return (
    <>
      <input
        type="search"
        placeholder="Search notes…"
        value={query}
        onChange={handleQueryChange}
        aria-label="Search notes"
      />

      {isSearching && (
        <p>
          {searchResults.total} result{searchResults.total !== 1 ? 's' : ''} for &ldquo;{query}
          &rdquo;
        </p>
      )}

      {displayNotes.length === 0 ? (
        <p>{isSearching ? 'No matching notes.' : 'No notes yet.'}</p>
      ) : (
        <ul>
          {displayNotes.map((note) =>
            editingId === note.id ? (
              <li key={note.id}>
                <input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                <input value={editContent} onChange={(e) => setEditContent(e.target.value)} />
                <button onClick={() => handleSave(note.id)}>Save</button>
                <button onClick={() => setEditingId(null)}>Cancel</button>
              </li>
            ) : (
              <li key={note.id}>
                <strong>{note.title}</strong>: {note.content}
                <button onClick={() => startEdit(note)}>Edit</button>
                <button onClick={() => handleDelete(note.id)}>Delete</button>
              </li>
            )
          )}
        </ul>
      )}

      {isSearching && totalPages > 1 && (
        <div>
          <button disabled={page <= 1} onClick={() => runSearch(query, page - 1)}>
            Prev
          </button>
          <span>
            {' '}
            Page {page} of {totalPages}{' '}
          </span>
          <button disabled={page >= totalPages} onClick={() => runSearch(query, page + 1)}>
            Next
          </button>
        </div>
      )}
    </>
  )
})

export default NotesList
