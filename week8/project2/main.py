"""
Developer Control Center - FastHTML Application
A full-stack Python web application for managing notes and action items.
"""
from fasthtml.common import *
from routers.notes import setup_notes_routes, notes_list
from routers.action_items import setup_action_items_routes, action_items_list

app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css"),
    ),
    pico=False
)

setup_notes_routes(app)
setup_action_items_routes(app)


def header():
    """Application header."""
    return Header(
        Div(
            H1("Developer Control Center", style="margin-bottom: 0;"),
            P("Manage your notes and action items with auto-extraction", style="margin-top: 5px; opacity: 0.8;"),
            cls="container",
            style="padding: 20px 0;"
        ),
        style="background: var(--primary); color: white; margin-bottom: 30px;"
    )


def notes_section():
    """Notes section with create form and list."""
    return Section(
        H2("📝 Notes"),
        Article(
            Form(
                Fieldset(
                    Label("Title", Input(name="title", placeholder="Enter note title", required=True)),
                    Label(
                        "Content",
                        Textarea(
                            name="content",
                            placeholder="Enter content... Use #tags and action items like:\n- [ ] task\ntodo: something\nNeed to do this!\nImportant!",
                            rows=6,
                            required=True
                        )
                    ),
                ),
                Button("Create Note", type="submit", cls="primary"),
                hx_post="/notes",
                hx_target="#notes-list",
                hx_swap="innerHTML",
                hx_on="htmx:afterRequest: this.reset()"
            ),
            style="margin-bottom: 30px;"
        ),
        Div(
            Form(
                Input(
                    name="search",
                    placeholder="Search notes...",
                    type="search",
                    hx_get="/notes",
                    hx_trigger="keyup changed delay:300ms",
                    hx_target="#notes-list",
                    hx_swap="innerHTML"
                ),
                style="margin-bottom: 20px;"
            )
        ),
        Div(notes_list(), id="notes-list-container"),
        style="margin-bottom: 50px;"
    )


def action_items_section():
    """Action items section with create form and list."""
    return Section(
        H2("✓ Action Items"),
        Article(
            Form(
                Fieldset(
                    Label(
                        "Description",
                        Input(
                            name="description",
                            placeholder="Enter action item description",
                            required=True
                        )
                    ),
                ),
                Button("Add Action Item", type="submit", cls="primary"),
                hx_post="/action-items",
                hx_target="#action-items-list",
                hx_swap="outerHTML",
                hx_on="htmx:afterRequest: this.reset()"
            ),
            style="margin-bottom: 30px;"
        ),
        Div(
            Label(
                Input(
                    type="checkbox",
                    name="completed_only",
                    value="true",
                    hx_get="/action-items",
                    hx_trigger="change",
                    hx_target="#action-items-list",
                    hx_swap="outerHTML",
                    hx_include="this"
                ),
                "Show completed only",
                style="margin-bottom: 20px;"
            )
        ),
        Div(action_items_list(), id="action-items-list-container"),
    )


def footer():
    """Application footer."""
    return Footer(
        Div(
            P(
                "Built with ",
                A("FastHTML", href="https://fastht.ml", target="_blank"),
                " and ",
                A("Supabase", href="https://supabase.com", target="_blank"),
                style="text-align: center; opacity: 0.7; margin-top: 50px;"
            ),
            cls="container"
        )
    )


@rt("/")
def get():
    """Main application page."""
    return Title("Developer Control Center"), Main(
        header(),
        Div(
            notes_section(),
            Hr(),
            action_items_section(),
            cls="container"
        ),
        footer()
    )


if __name__ == "__main__":
    serve()
