# Developer Control Center

A full-stack web application built with Next.js that helps developers organize notes, automatically extract tags and action items, and manage their workflow efficiently.

## Features

### Notes Management
- Create, read, update, and delete notes
- Rich text content support
- Search functionality to filter notes by title or content
- Automatic tag extraction from hashtags (e.g., #python, #react)
- Automatic action item extraction from note content
- Real-time tag association

### Action Items Management
- Automatically extracted from notes or manually created
- Toggle completion status with visual feedback
- Filter to show completed items only
- Delete unwanted action items
- Track creation and update timestamps

### Auto-Extraction Features

The application automatically parses note content to extract:

#### Tags
- Any word prefixed with `#` (hashtag) is automatically extracted as a tag
- Example: `#python`, `#javascript`, `#react`
- Tags are case-insensitive and stored in lowercase
- Automatically linked to notes via many-to-many relationship

#### Action Items
The system recognizes several action item formats:

1. **Checkbox syntax**: `- [ ]` or `* [ ]`
   - Example: `- [ ] Complete the documentation`

2. **Prefix keywords** (case-insensitive):
   - `TODO:` - Example: `TODO: Fix the bug`
   - `ACTION:` - Example: `ACTION: Review pull request`
   - `FIXME:` - Example: `FIXME: Refactor this function`
   - `NOTE:` - Example: `NOTE: Check with team`
   - `FOLLOW UP:` - Example: `FOLLOW UP: Send email to client`

3. **Imperative verbs** (case-insensitive):
   - `Need to` - Example: `Need to update dependencies`
   - `Should` - Example: `Should add unit tests`
   - `Must` - Example: `Must deploy before Friday`
   - `Please` - Example: `Please review the code`

4. **Exclamation mark**: Any line ending with `!`
   - Example: `Deploy to production!`

## Tech Stack

- **Framework**: Next.js 13 (App Router)
- **Language**: TypeScript
- **Database**: Supabase (PostgreSQL)
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI (via shadcn/ui)
- **Icons**: Lucide React

## Database Schema

### Tables

#### `notes`
- `id` (uuid, primary key)
- `title` (text, required)
- `content` (text, required)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

#### `tags`
- `id` (uuid, primary key)
- `name` (text, unique, required)
- `created_at` (timestamptz)

#### `action_items`
- `id` (uuid, primary key)
- `description` (text, required)
- `completed` (boolean, default: false)
- `note_id` (uuid, foreign key to notes, nullable)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

#### `note_tags`
- `note_id` (uuid, foreign key to notes)
- `tag_id` (uuid, foreign key to tags)
- Primary key: combination of (note_id, tag_id)

### Relationships
- Notes and Tags: Many-to-Many (via note_tags junction table)
- Notes and Action Items: One-to-Many (cascade delete)

## Prerequisites

- Node.js 18+ and npm
- A Supabase account and project

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

The `.env` file should already contain your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. Database Setup

The database schema and sample data have already been applied via Supabase migrations. Your database includes:

- All required tables (notes, tags, action_items, note_tags)
- Row Level Security (RLS) policies
- Sample data for testing (5 notes with tags and action items)

To verify your database setup, you can check the Supabase dashboard or use the application to view the sample data.

### 4. Run the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### 5. Build for Production

```bash
npm run build
npm start
```

## API Routes

### Notes

- `GET /api/notes` - Get all notes (with optional search query parameter)
- `GET /api/notes?search=keyword` - Search notes by title or content
- `POST /api/notes` - Create a new note (auto-extracts tags and action items)
- `GET /api/notes/[id]` - Get a specific note
- `PUT /api/notes/[id]` - Update a note (re-extracts tags and action items)
- `DELETE /api/notes/[id]` - Delete a note

### Action Items

- `GET /api/action-items` - Get all action items
- `GET /api/action-items?completedOnly=true` - Get only completed action items
- `POST /api/action-items` - Create a new action item
- `GET /api/action-items/[id]` - Get a specific action item
- `PUT /api/action-items/[id]` - Update an action item (toggle completion or edit description)
- `DELETE /api/action-items/[id]` - Delete an action item

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── notes/
│   │   │   ├── route.ts           # Notes list and create
│   │   │   └── [id]/route.ts      # Note detail, update, delete
│   │   └── action-items/
│   │       ├── route.ts           # Action items list and create
│   │       └── [id]/route.ts      # Action item detail, update, delete
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx                   # Main dashboard
├── components/
│   ├── notes/
│   │   ├── note-form.tsx          # Create note form
│   │   ├── note-list.tsx          # Notes display with search
│   │   └── note-edit-dialog.tsx   # Edit note dialog
│   ├── action-items/
│   │   ├── action-item-form.tsx   # Create action item form
│   │   └── action-item-list.tsx   # Action items display with filter
│   └── ui/                        # Shadcn UI components
├── lib/
│   ├── supabase.ts                # Supabase client and types
│   ├── extraction.ts              # Tag and action item extraction logic
│   └── utils.ts                   # Utility functions
└── README.md
```

## Usage Guide

### Creating a Note with Auto-Extraction

1. Enter a note title
2. Write your content including:
   - Hashtags for tags (e.g., `#development #planning`)
   - Action items in any supported format
3. Click "Create Note"
4. The system will automatically:
   - Extract and create/link tags
   - Parse and create action items
   - Associate action items with the note

Example note content:
```
Planning the new #nextjs #typescript project.

- [ ] Set up project repository
TODO: Configure ESLint and Prettier
Need to create database schema
Must review security best practices!
```

This will create:
- Tags: nextjs, typescript
- Action items:
  - Set up project repository
  - Configure ESLint and Prettier
  - create database schema
  - review security best practices

### Searching Notes

Use the search bar in the Notes section to filter by title or content. The search is case-insensitive and updates in real-time.

### Managing Action Items

- Click the circle icon to mark an item as complete (or incomplete)
- Toggle "Show completed only" to filter the view
- Click the trash icon to delete an action item
- Manually add action items using the form (independent of notes)

### Editing Notes

1. Click the edit icon on any note
2. Modify the title or content
3. Click "Save Changes"
4. Tags and action items are automatically re-extracted based on new content

## Development

### Type Checking

```bash
npm run typecheck
```

### Linting

```bash
npm run lint
```

### Building

```bash
npm run build
```

## Security

The application uses Supabase Row Level Security (RLS) with public access policies for demonstration purposes. In a production environment, you should:

1. Implement proper authentication
2. Restrict RLS policies to authenticated users
3. Add user ownership checks to all policies
4. Validate and sanitize all user inputs
5. Implement rate limiting on API routes

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
