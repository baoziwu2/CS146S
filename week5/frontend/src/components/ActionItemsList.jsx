import { useState, useEffect } from 'react'

export default function ActionItemsList() {
  const [items, setItems] = useState([])

  async function loadItems() {
    const res = await fetch('/action-items/')
    if (!res.ok) return
    setItems(await res.json())
  }

  useEffect(() => {
    loadItems()
  }, [])

  async function handleComplete(id) {
    await fetch(`/action-items/${id}/complete`, { method: 'PUT' })
    loadItems()
  }

  if (items.length === 0) {
    return <p>No action items yet.</p>
  }

  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>
          <span>{item.description}</span>
          {' '}[{item.completed ? 'done' : 'open'}]
          {!item.completed && (
            <button onClick={() => handleComplete(item.id)}>Complete</button>
          )}
        </li>
      ))}
    </ul>
  )
}
