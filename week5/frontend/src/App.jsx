import { useRef, useState, useEffect } from 'react'
import NotesList from './components/NotesList'
import NoteForm from './components/NoteForm'
import ActionItemsList from './components/ActionItemsList'
import ActionItemForm from './components/ActionItemForm'

export default function App() {
  const notesListRef = useRef(null)
  const actionsListRef = useRef(null)

  const [tags, setTags] = useState([])
  const [selectedTagId, setSelectedTagId] = useState(null)

  async function reloadTags() {
    const r = await fetch('/tags/')
    if (r.ok) setTags((await r.json()).data)
  }

  useEffect(() => {
    reloadTags()
  }, [])

  return (
    <>
      <header className="app-header">
        <span className="app-header-icon">📝</span>
        <h1>Modern Software Dev Starter</h1>
      </header>

      <div className="app-body">
        {/* ── Notes column ── */}
        <section className="card">
          <div className="card-header">
            <span className="card-header-icon">🗒️</span>
            <h2>Notes</h2>
          </div>
          <div className="card-body">
            <NoteForm
              onCreated={() => {
                notesListRef.current?.reload()
                reloadTags()
              }}
            />

            {tags.length > 0 && (
              <div className="filter-bar" role="group" aria-label="Filter notes by tag">
                <button
                  className="btn btn-ghost btn-sm btn-pill"
                  onClick={() => setSelectedTagId(null)}
                  aria-pressed={selectedTagId === null}
                >
                  All tags
                </button>
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    className="btn btn-ghost btn-sm btn-pill"
                    onClick={() => setSelectedTagId(tag.id)}
                    aria-pressed={selectedTagId === tag.id}
                  >
                    #{tag.name}
                  </button>
                ))}
              </div>
            )}

            <NotesList ref={notesListRef} tagId={selectedTagId} onTagsChanged={reloadTags} />
          </div>
        </section>

        {/* ── Action Items column ── */}
        <section className="card">
          <div className="card-header">
            <span className="card-header-icon">✅</span>
            <h2>Action Items</h2>
          </div>
          <div className="card-body">
            <ActionItemForm onCreated={() => actionsListRef.current?.reload()} />
            <ActionItemsList ref={actionsListRef} />
          </div>
        </section>
      </div>
    </>
  )
}
