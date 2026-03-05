"""
Routes and UI components for Notes CRUD operations.
"""
from fasthtml.common import *
from models import Note


def render_note_card(note):
    """Render a single note card."""
    tags_html = Div(
        *[
            Span(f"#{tag['name']}", cls="badge", style="margin-right: 5px;")
            for tag in note.get('tags', [])
        ],
        style="margin-top: 10px;"
    ) if note.get('tags') else None

    return Article(
        H4(note['title']),
        P(note['content'], style="white-space: pre-wrap;"),
        tags_html,
        Div(
            Button(
                "Edit",
                hx_get=f"/notes/{note['id']}/edit",
                hx_target=f"#note-{note['id']}",
                hx_swap="outerHTML",
                cls="secondary"
            ),
            Button(
                "Delete",
                hx_delete=f"/notes/{note['id']}",
                hx_target=f"#note-{note['id']}",
                hx_swap="outerHTML",
                hx_confirm="Are you sure you want to delete this note?",
                cls="contrast"
            ),
            style="margin-top: 10px;"
        ),
        id=f"note-{note['id']}",
        style="margin-bottom: 20px;"
    )


def render_note_edit_form(note):
    """Render the edit form for a note."""
    return Article(
        Form(
            Label("Title", Input(name="title", value=note['title'], required=True)),
            Label("Content", Textarea(note['content'], name="content", rows=6, required=True)),
            Div(
                Button("Save", type="submit", cls="primary"),
                Button(
                    "Cancel",
                    hx_get=f"/notes/{note['id']}",
                    hx_target=f"#note-{note['id']}",
                    hx_swap="outerHTML",
                    cls="secondary"
                ),
                style="display: flex; gap: 10px;"
            ),
            hx_put=f"/notes/{note['id']}",
            hx_target=f"#note-{note['id']}",
            hx_swap="outerHTML"
        ),
        id=f"note-{note['id']}",
        style="margin-bottom: 20px;"
    )


def notes_list(search: str = None):
    """Render the list of all notes."""
    notes = Note.get_all(search)

    if not notes:
        return Div(
            P("No notes found." if not search else f"No notes found for '{search}'."),
            id="notes-list"
        )

    return Div(
        *[render_note_card(note) for note in notes],
        id="notes-list"
    )


def setup_notes_routes(app):
    """Setup all note-related routes."""

    @app.get("/notes")
    def get_notes(search: str = None):
        return notes_list(search)

    @app.post("/notes")
    def create_note(title: str, content: str):
        note = Note.create(title, content)
        app.get('/').invalidate()
        return notes_list()

    @app.get("/notes/{note_id}")
    def get_note(note_id: str):
        note = Note.get_by_id(note_id)
        if note:
            return render_note_card(note)
        return P("Note not found")

    @app.get("/notes/{note_id}/edit")
    def edit_note_form(note_id: str):
        note = Note.get_by_id(note_id)
        if note:
            return render_note_edit_form(note)
        return P("Note not found")

    @app.put("/notes/{note_id}")
    def update_note(note_id: str, title: str, content: str):
        note = Note.update(note_id, title, content)
        if note:
            note = Note.get_by_id(note_id)
            return render_note_card(note)
        return P("Note not found")

    @app.delete("/notes/{note_id}")
    def delete_note(note_id: str):
        Note.delete(note_id)
        return ""
