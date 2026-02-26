import { useState, useEffect } from 'react'

export default function NotesList() {
  const [notes, setNotes] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')

  async function loadNotes() {
    const res = await fetch('/notes/')
    if (!res.ok) return
    setNotes(await res.json())
  }

  useEffect(() => {
    loadNotes()
  }, [])

  async function handleDelete(id) {
    await fetch(`/notes/${id}`, { method: 'DELETE' })
    loadNotes()
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
  }

  if (notes.length === 0) {
    return <p>No notes yet.</p>
  }

  return (
    <ul>
      {notes.map((note) =>
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
  )
}
