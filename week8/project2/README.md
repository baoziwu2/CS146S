# Developer Control Center

A full-stack web application built entirely in Python using FastHTML for managing notes and action items with intelligent auto-extraction capabilities.

## Features

- **Notes Management**: Create, read, update, and delete notes with full-text search
- **Auto-Tag Extraction**: Automatically extracts and links hashtags from note content
- **Auto-Action Item Extraction**: Intelligently extracts action items from notes using pattern matching:
  - Checkbox syntax: `- [ ]` or `* [ ]`
  - Prefixes: `todo:`, `action:`, `fixme:`, `note:`, `follow up:`
  - Imperative verbs: `need to`, `should`, `must`, `please`
  - Exclamation marks: Lines ending with `!`
- **Action Items Management**: Manual creation, completion tracking, and filtering
- **Real-time Updates**: HTMX-powered interface with no page reloads
- **Clean UI**: Built with Pico CSS for a modern, responsive design

## Architecture

The application follows a clean, modular architecture:

```
project/
├── main.py                    # Application entry point and UI
├── db.py                      # Supabase database client
├── models.py                  # Data models and database operations
├── services/
│   ├── __init__.py
│   └── extract.py            # Auto-extraction logic
├── routers/
│   ├── __init__.py
│   ├── notes.py              # Notes CRUD routes
│   └── action_items.py       # Action items CRUD routes
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.10 or higher
- A Supabase account and project (database is pre-configured)

## Installation

### 1. Clone or Download the Project

```bash
cd project
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

The `.env` file should already contain your Supabase credentials:
- `VITE_SUPABASE_URL`: Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous key

## Running the Application

Start the development server:

```bash
python main.py
```

The application will be available at `http://localhost:5001`

## Usage Guide

### Creating Notes

1. Enter a title and content in the "Notes" section
2. Use hashtags (e.g., `#python`, `#fasthtml`) to categorize your notes
3. Add action items using any of these patterns:
   - `- [ ] Task to complete`
   - `todo: Something to do`
   - `Need to implement this feature`
   - `Important task!`
4. Click "Create Note" - tags and action items are automatically extracted

### Managing Notes

- **Search**: Use the search box to filter notes by title or content
- **Edit**: Click the "Edit" button to modify a note
- **Delete**: Click the "Delete" button to remove a note

### Managing Action Items

- **Create Manually**: Add action items directly using the form
- **Auto-Extracted**: Action items from notes appear automatically
- **Toggle Completion**: Click the checkbox to mark items as done
- **Filter**: Use "Show completed only" to view finished tasks
- **Delete**: Click the × button to remove an item

## Database Schema

### Tables

- **notes**: Stores note content with title, content, and timestamps
- **tags**: Unique tag names extracted from notes
- **note_tags**: Many-to-many relationship between notes and tags
- **action_items**: Task items with description, completion status, and optional note reference

### Auto-Extraction Examples

**Input Note Content:**
```
Working on #python #fasthtml project

- [ ] Implement user authentication
todo: Add error handling
Need to write unit tests
Deploy to production!
```

**Extracted Tags:**
- python
- fasthtml

**Extracted Action Items:**
- Implement user authentication
- Add error handling
- Need to write unit tests
- Deploy to production!

## Technology Stack

- **FastHTML**: Pure Python web framework for building interactive web UIs
- **Supabase**: PostgreSQL database with real-time capabilities
- **HTMX**: Dynamic HTML updates without full page reloads
- **Pico CSS**: Minimal CSS framework for clean styling

## Development Notes

- All UI components are built using FastHTML's Pythonic API (no separate HTML/CSS/JS files)
- HTMX is used for seamless partial page updates
- Row Level Security (RLS) is enabled on all database tables
- The application uses public access policies for demo purposes

## License

MIT License - Feel free to use and modify as needed.
