import { useState, useEffect, useImperativeHandle, forwardRef } from 'react'

const PAGE_SIZE = 10

const FILTERS = [
  { key: 'all', label: 'All', param: '' },
  { key: 'pending', label: 'Pending', param: '?completed=false' },
  { key: 'done', label: 'Done', param: '?completed=true' },
]

const ActionItemsList = forwardRef(function ActionItemsList(_, ref) {
  const [results, setResults] = useState({ items: [], total: 0, page: 1, page_size: PAGE_SIZE })
  const [filter, setFilter] = useState('all')
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [page, setPage] = useState(1)

  async function loadItems(f = filter, p = 1) {
    const { param } = FILTERS.find((x) => x.key === f)
    const sep = param ? '&' : '?'
    const res = await fetch(`/action-items/${param}${sep}page=${p}&page_size=${PAGE_SIZE}`)
    if (!res.ok) return
    setResults((await res.json()).data)
    setSelectedIds(new Set())
    setPage(p)
  }

  useEffect(() => {
    loadItems()
  }, [])

  useImperativeHandle(ref, () => ({
    reload: () => loadItems(filter, page),
  }))

  async function handleComplete(id) {
    await fetch(`/action-items/${id}/complete`, { method: 'PUT' })
    loadItems(filter, page)
  }

  async function handleBulkComplete() {
    if (selectedIds.size === 0) return
    const res = await fetch('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [...selectedIds] }),
    })
    if (res.ok) loadItems(filter, page)
  }

  function handleFilterChange(f) {
    setFilter(f)
    setPage(1)
    loadItems(f, 1)
  }

  function toggleSelect(id) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const totalPages = Math.ceil(results.total / PAGE_SIZE)

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

      {results.items.length === 0 ? (
        <p>No action items yet.</p>
      ) : (
        <ul>
          {results.items.map((item) => (
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

      {totalPages > 1 && (
        <div>
          <button disabled={page <= 1} onClick={() => loadItems(filter, page - 1)}>
            Prev
          </button>
          <span>
            {' '}
            Page {page} of {totalPages}{' '}
          </span>
          <button disabled={page >= totalPages} onClick={() => loadItems(filter, page + 1)}>
            Next
          </button>
        </div>
      )}
    </>
  )
})

export default ActionItemsList
