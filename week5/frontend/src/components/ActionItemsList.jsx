import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'

const FILTERS = [
  { key: 'all', label: 'All', param: '' },
  { key: 'pending', label: 'Pending', param: '?completed=false' },
  { key: 'done', label: 'Done', param: '?completed=true' },
]

const ActionItemsList = forwardRef(function ActionItemsList(_, ref) {
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState('all')
  const [selectedIds, setSelectedIds] = useState(new Set())

  async function loadItems(f = filter) {
    const { param } = FILTERS.find((x) => x.key === f)
    const res = await fetch(`/action-items/${param}`)
    if (!res.ok) return
    setItems((await res.json()).data)
    setSelectedIds(new Set())
  }

  useEffect(() => {
    loadItems()
  }, [])

  useImperativeHandle(ref, () => ({
    reload: () => loadItems(),
  }))

  async function handleComplete(id) {
    await fetch(`/action-items/${id}/complete`, { method: 'PUT' })
    loadItems()
  }

  async function handleBulkComplete() {
    if (selectedIds.size === 0) return
    const res = await fetch('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [...selectedIds] }),
    })
    if (res.ok) loadItems()
  }

  function handleFilterChange(f) {
    setFilter(f)
    loadItems(f)
  }

  function toggleSelect(id) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <>
      <div role="group" aria-label="Filter action items">
        {FILTERS.map(({ key, label }) => (
          <button key={key} onClick={() => handleFilterChange(key)} aria-pressed={filter === key}>
            {label}
          </button>
        ))}
      </div>

      {selectedIds.size > 0 && (
        <button onClick={handleBulkComplete}>
          Complete Selected ({selectedIds.size})
        </button>
      )}

      {items.length === 0 ? (
        <p>No action items yet.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id}>
              {!item.completed && (
                <input
                  type="checkbox"
                  checked={selectedIds.has(item.id)}
                  onChange={() => toggleSelect(item.id)}
                  aria-label={`Select ${item.description}`}
                />
              )}
              <span>{item.description}</span>
              {' '}
              [{item.completed ? 'done' : 'open'}]
              {!item.completed && (
                <button onClick={() => handleComplete(item.id)}>Complete</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  )
})

export default ActionItemsList
