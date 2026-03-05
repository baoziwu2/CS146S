"""
Routes and UI components for Action Items CRUD operations.
"""
from fasthtml.common import *
from models import ActionItem


def render_action_item(item):
    """Render a single action item."""
    checkbox_style = "text-decoration: line-through; opacity: 0.6;" if item['completed'] else ""

    return Li(
        Div(
            Input(
                type="checkbox",
                checked=item['completed'],
                hx_post=f"/action-items/{item['id']}/toggle",
                hx_target=f"#item-{item['id']}",
                hx_swap="outerHTML",
                style="margin-right: 10px;"
            ),
            Span(item['description'], style=checkbox_style),
            Button(
                "×",
                hx_delete=f"/action-items/{item['id']}",
                hx_target=f"#item-{item['id']}",
                hx_swap="outerHTML",
                hx_confirm="Delete this action item?",
                cls="contrast",
                style="margin-left: 10px; padding: 2px 8px; font-size: 1.2em;"
            ),
            style="display: flex; align-items: center;"
        ),
        id=f"item-{item['id']}",
        style="margin-bottom: 10px; list-style: none;"
    )


def action_items_list(completed_only: bool = False):
    """Render the list of all action items."""
    items = ActionItem.get_all(completed_only)

    if not items:
        return Div(
            P("No action items found." if not completed_only else "No completed action items."),
            id="action-items-list"
        )

    return Ul(
        *[render_action_item(item) for item in items],
        id="action-items-list",
        style="padding-left: 0;"
    )


def setup_action_items_routes(app):
    """Setup all action item-related routes."""

    @app.get("/action-items")
    def get_action_items(completed_only: str = "false"):
        completed = completed_only.lower() == "true"
        return action_items_list(completed)

    @app.post("/action-items")
    def create_action_item(description: str):
        ActionItem.create(description)
        return action_items_list()

    @app.post("/action-items/{item_id}/toggle")
    def toggle_action_item(item_id: str):
        item = ActionItem.toggle_completed(item_id)
        if item:
            return render_action_item(item)
        return P("Action item not found")

    @app.delete("/action-items/{item_id}")
    def delete_action_item(item_id: str):
        ActionItem.delete(item_id)
        return ""
