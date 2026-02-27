import { useState } from 'react'

export default function ActionItemForm({ onCreated }) {
  const [description, setDescription] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const res = await fetch('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    })
    if (!res.ok) return
    setDescription('')
    onCreated?.()
  }

  return (
    <form onSubmit={handleSubmit} className="form-row" style={{ marginBottom: '1rem' }}>
      <input
        type="text"
        placeholder="New action item…"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
        aria-label="Action item description"
      />
      <button type="submit" className="btn btn-primary">
        + Add
      </button>
    </form>
  )
}
