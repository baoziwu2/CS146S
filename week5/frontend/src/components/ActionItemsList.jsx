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
      <div className="filter-bar" role="group" aria-label="Filter action items">
        {FILTERS.map(({ key, label }) => (
          <button
            key={key}
            className="btn btn-ghost btn-sm btn-pill"
            onClick={() => handleFilterChange(key)}
            aria-pressed={filter === key}
          >
            {label}
          </button>
        ))}
      </div>

      {selectedIds.size > 0 && (
        <div className="bulk-bar">
          <span>{selectedIds.size} selected</span>
          <button className="btn btn-success btn-sm" onClick={handleBulkComplete}>
            ✓ Complete Selected
          </button>
        </div>
      )}

      {results.items.length === 0 ? (
        <div className="empty-state">
          <span className="empty-state-icon">✅</span>
          {filter === 'done' ? 'Nothing completed yet.' : 'No action items yet.'}
        </div>
      ) : (
        <div className="action-list">
          {results.items.map((item) => (
            <div key={item.id} className={`action-item${item.completed ? ' action-done' : ''}`}>
              {!item.completed && (
                <input
                  type="checkbox"
                  checked={selectedIds.has(item.id)}
                  onChange={() => toggleSelect(item.id)}
                  aria-label={`Select ${item.description}`}
                />
              )}
              {item.completed && <span style={{ width: '1rem', flexShrink: 0 }} />}
              <span className="action-desc">{item.description}</span>
              <span className={`action-badge ${item.completed ? 'action-badge-done' : 'action-badge-open'}`}>
                {item.completed ? 'done' : 'open'}
              </span>
              {!item.completed && (
                <button
                  className="btn btn-success btn-sm"
                  onClick={() => handleComplete(item.id)}
                  title="Mark complete"
                >
                  ✓
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn-ghost btn-sm"
            disabled={page <= 1}
            onClick={() => loadItems(filter, page - 1)}
          >
            ← Prev
          </button>
          <span className="pagination-label">
            {page} / {totalPages}
          </span>
          <button
            className="btn btn-ghost btn-sm"
            disabled={page >= totalPages}
            onClick={() => loadItems(filter, page + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </>
  )
})

export default ActionItemsList
