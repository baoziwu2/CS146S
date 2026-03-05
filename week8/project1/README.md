# Developer Control Center

A clean, production-ready web application for managing developer notes and action items. Built with React, TypeScript, Tailwind CSS, and Supabase.

---

## Features

- **Notes**: Create, read, update, and delete notes with title and content. Supports full-text keyword search across title and content, sorting by title, created date, or last updated, and pagination.
- **Action Items**: Create, toggle complete/reopen, and delete action items. Filter by "completed only", sort by description or date, and paginate.
- **Validation**: Required fields are enforced on the frontend before any database operation.
- **Tags**: Data model supports many-to-many note tagging via the `note_tags` junction table (UI coming soon).

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or higher
- npm v9 or higher
- A [Supabase](https://supabase.com/) project (free tier is sufficient)

---

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
```

You can find these values in your Supabase project dashboard under **Project Settings > API**.

---

## Database Setup

The database schema is managed via Supabase migrations. The following tables are created automatically:

| Table | Description |
|---|---|
| `notes` | Developer notes with title and content |
| `tags` | Reusable tags for notes |
| `note_tags` | Many-to-many join table linking notes and tags |
| `action_items` | Trackable tasks with a completion status |

All tables have Row Level Security (RLS) enabled. The default policies allow access using the `anon` public key, which is suitable for single-user or internal tooling use. For multi-user applications, update the RLS policies to scope data per `auth.uid()`.

If you are setting up a fresh Supabase project, apply the migration file located at:

```
supabase/migrations/create_developer_control_center_schema.sql
```

You can run it directly in the Supabase SQL Editor or via the Supabase CLI:

```bash
supabase db push
```

---

## Setup & Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Configure environment variables (see above)
cp .env.example .env
# Then edit .env with your Supabase credentials

# 3. Start the development server
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start the Vite development server with hot module replacement |
| `npm run build` | Build the production bundle to the `dist/` directory |
| `npm run preview` | Serve the production build locally for testing |
| `npm run lint` | Run ESLint across all source files |
| `npm run typecheck` | Run TypeScript type checking without emitting files |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript |
| Styling | Tailwind CSS 3 |
| Icons | Lucide React |
| Build Tool | Vite 5 |
| Database | Supabase (PostgreSQL) |
| DB Client | @supabase/supabase-js v2 |

---

## Data Models

### Note
```
id          uuid        Primary key
title       text        Required
content     text        Optional
created_at  timestamptz Auto-set on insert
updated_at  timestamptz Auto-updated on change
```

### Tag
```
id          uuid        Primary key
name        text        Unique, required
created_at  timestamptz Auto-set on insert
updated_at  timestamptz Auto-updated on change
```

### Note_Tags (junction)
```
note_id     uuid        FK -> notes.id (cascade delete)
tag_id      uuid        FK -> tags.id (cascade delete)
```

### ActionItem
```
id          uuid        Primary key
description text        Required
completed   boolean     Default false
created_at  timestamptz Auto-set on insert
updated_at  timestamptz Auto-updated on change
```

---

## Project Structure

```
src/
├── components/
│   ├── actionItems/
│   │   ├── ActionItemForm.tsx      # Create form for action items
│   │   ├── ActionItemRow.tsx       # Single row with toggle/delete
│   │   └── ActionItemsSection.tsx  # Full section with filters/pagination
│   ├── notes/
│   │   ├── NoteCard.tsx            # Note card with edit/delete
│   │   ├── NoteForm.tsx            # Create/edit form for notes
│   │   └── NotesSection.tsx        # Full section with search/pagination
│   └── ui/
│       ├── Button.tsx              # Reusable button with variants
│       ├── ConfirmDialog.tsx       # Delete confirmation modal
│       ├── EmptyState.tsx          # Empty list state display
│       ├── Modal.tsx               # Generic modal wrapper
│       ├── Pagination.tsx          # Page navigation controls
│       └── SortSelect.tsx          # Sort field and order selects
├── lib/
│   └── supabaseClient.ts           # Supabase singleton client
├── services/
│   ├── actionItemsService.ts       # CRUD for action items
│   └── notesService.ts             # CRUD for notes
├── types/
│   └── index.ts                    # Shared TypeScript interfaces
├── App.tsx                         # Root component with tab navigation
├── index.css                       # Global styles + animations
└── main.tsx                        # React entry point
```
