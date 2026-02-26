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
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <button type="submit">Add Action Item</button>
    </form>
  )
}
