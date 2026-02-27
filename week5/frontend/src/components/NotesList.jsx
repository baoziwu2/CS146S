import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'

const PAGE_SIZE = 5

const NotesList = forwardRef(function NotesList({ tagId = null, onTagsChanged }, ref) {
  const [results, setResults] = useState({ items: [], total: 0, page: 1, page_size: PAGE_SIZE })
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)

  const isSearching = query.length > 0

  async function loadNotes(p = 1) {
    const params = new URLSearchParams({ page: p, page_size: PAGE_SIZE })
    if (tagId !== null) params.set('tag_id', tagId)
    const res = await fetch(`/notes/?${params}`)
    if (!res.ok) return
    setResults((await res.json()).data)
    setPage(p)
  }

  async function runSearch(q, p = 1) {
    const params = new URLSearchParams({ q, page: p, page_size: PAGE_SIZE, sort: 'created_desc' })
    if (tagId !== null) params.set('tag_id', tagId)
    const res = await fetch(`/notes/search/?${params}`)
    if (!res.ok) return
    setResults((await res.json()).data)
    setPage(p)
  }

  useEffect(() => {
    loadNotes(1)
    setPage(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tagId])

  useImperativeHandle(ref, () => ({
    reload: () => {
      if (isSearching) runSearch(query, page)
      else loadNotes(page)
    },
  }))

  async function handleDelete(id) {
    const prev = results
    setResults((r) => ({ ...r, items: r.items.filter((n) => n.id !== id), total: r.total - 1 }))
    const res = await fetch(`/notes/${id}`, { method: 'DELETE' })
    if (!res.ok) setResults(prev)
  }

  function startEdit(note) {
    setEditingId(note.id)
    setEditTitle(note.title)
    setEditContent(note.content)
  }

  async function handleSave(id) {
    const prev = results
    const updated = { id, title: editTitle, content: editContent }
    setResults((r) => ({ ...r, items: r.items.map((n) => (n.id === id ? { ...n, ...updated } : n)) }))
    setEditingId(null)
    const res = await fetch(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: editTitle, content: editContent }),
    })
    if (!res.ok) {
      setResults(prev)
      setEditingId(id)
    } else if (/#\w/.test(editTitle) || /#\w/.test(editContent) || /- \[ \]/.test(editContent)) {
      await fetch(`/notes/${id}/extract?apply=true`, { method: 'POST' })
      loadNotes(page)
      onTagsChanged?.()
    }
  }

  function handleQueryChange(e) {
    const q = e.target.value
    setQuery(q)
    setPage(1)
    if (q) runSearch(q, 1)
    else loadNotes(1)
  }

  function goToPage(p) {
    if (isSearching) runSearch(query, p)
    else loadNotes(p)
  }

  const totalPages = Math.ceil(results.total / PAGE_SIZE)

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
          {results.total} result{results.total !== 1 ? 's' : ''} for &ldquo;{query}&rdquo;
        </p>
      )}

      {results.items.length === 0 ? (
        <p>{isSearching ? 'No matching notes.' : 'No notes yet.'}</p>
      ) : (
        <ul>
          {results.items.map((note) =>
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
                {note.tags?.length > 0 && (
                  <span aria-label="tags">
                    {note.tags.map((t) => (
                      <span key={t.id} className="tag-chip">
                        {t.name}
                      </span>
                    ))}
                  </span>
                )}
                <button onClick={() => startEdit(note)}>Edit</button>
                <button onClick={() => handleDelete(note.id)}>Delete</button>
              </li>
            )
          )}
        </ul>
      )}

      {totalPages > 1 && (
        <div>
          <button disabled={page <= 1} onClick={() => goToPage(page - 1)}>
            Prev
          </button>
          <span>
            {' '}
            Page {page} of {totalPages}{' '}
          </span>
          <button disabled={page >= totalPages} onClick={() => goToPage(page + 1)}>
            Next
          </button>
        </div>
      )}
    </>
  )
})

export default NotesList
