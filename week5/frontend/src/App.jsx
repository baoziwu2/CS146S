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

  useEffect(() => {
    fetch('/tags')
      .then((r) => (r.ok ? r.json() : []))
      .then(setTags)
  }, [])

  return (
    <main>
      <h1>Modern Software Dev Starter</h1>

      <section>
        <h2>Notes</h2>
        <NoteForm onCreated={() => notesListRef.current?.reload()} />

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
                {tag.name}
              </button>
            ))}
          </div>
        )}

        <NotesList ref={notesListRef} tagId={selectedTagId} />
      </section>

      <section>
        <h2>Action Items</h2>
        <ActionItemForm onCreated={() => actionsListRef.current?.reload()} />
        <ActionItemsList ref={actionsListRef} />
      </section>
    </main>
  )
}
