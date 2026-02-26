import { useRef } from 'react'
import NotesList from './components/NotesList'
import NoteForm from './components/NoteForm'
import ActionItemsList from './components/ActionItemsList'
import ActionItemForm from './components/ActionItemForm'

export default function App() {
  const notesListRef = useRef(null)
  const actionsListRef = useRef(null)

  return (
    <main>
      <h1>Modern Software Dev Starter</h1>

      <section>
        <h2>Notes</h2>
        <NoteForm onCreated={() => notesListRef.current?.reload()} />
        <NotesList ref={notesListRef} />
      </section>

      <section>
        <h2>Action Items</h2>
        <ActionItemForm onCreated={() => actionsListRef.current?.reload()} />
        <ActionItemsList ref={actionsListRef} />
      </section>
    </main>
  )
}
