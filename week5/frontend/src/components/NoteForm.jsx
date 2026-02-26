import { useState } from 'react'

export default function NoteForm({ onCreated }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const res = await fetch('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    })
    if (!res.ok) return
    const note = await res.json()
    setTitle('')
    setContent('')
    // Auto-extract #hashtags and - [ ] tasks if any are present
    if (/#\w/.test(title) || /#\w/.test(content) || /- \[ \]/.test(content)) {
      await fetch(`/notes/${note.id}/extract?apply=true`, { method: 'POST' })
    }
    onCreated?.()
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        placeholder="Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
      />
      <button type="submit">Add Note</button>
    </form>
  )
}
