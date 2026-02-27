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
    <main>
      <h1>Modern Software Dev Starter</h1>

      <section>
        <h2>Notes</h2>
        <NoteForm
          onCreated={() => {
            notesListRef.current?.reload()
            reloadTags()
          }}
        />

        {tags.length > 0 && (
          <div role="group" aria-label="Filter notes by tag">
            <button
              onClick={() => setSelectedTagId(null)}
              aria-pressed={selectedTagId === null}
            >
              All tags
            </button>
            {tags.map((tag) => (
              <button
                key={tag.id}
                onClick={() => setSelectedTagId(tag.id)}
                aria-pressed={selectedTagId === tag.id}
              >
                #{tag.name}
              </button>
            ))}
          </div>
        )}

        <NotesList ref={notesListRef} tagId={selectedTagId} onTagsChanged={reloadTags} />
      </section>

      <section>
        <h2>Action Items</h2>
        <ActionItemForm onCreated={() => actionsListRef.current?.reload()} />
        <ActionItemsList ref={actionsListRef} />
      </section>
    </main>
  )
}
