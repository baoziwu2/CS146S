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
    setTitle('')
    setContent('')
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
