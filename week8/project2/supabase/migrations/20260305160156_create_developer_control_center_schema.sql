/*
  # Developer Control Center Schema

  ## Overview
  This migration creates the complete database schema for the Developer Control Center application,
  including tables for notes, tags, action items, and their relationships.

  ## Tables Created

  1. **notes**
     - `id` (uuid, primary key) - Unique identifier for each note
     - `title` (text, required) - Title of the note
     - `content` (text, required) - Full content of the note (markdown/plain text)
     - `created_at` (timestamptz) - Timestamp when note was created
     - `updated_at` (timestamptz) - Timestamp when note was last updated

  2. **tags**
     - `id` (uuid, primary key) - Unique identifier for each tag
     - `name` (text, unique, required) - Tag name (e.g., "python", "fasthtml")
     - `created_at` (timestamptz) - Timestamp when tag was created

  3. **action_items**
     - `id` (uuid, primary key) - Unique identifier for each action item
     - `description` (text, required) - Description of the action item
     - `completed` (boolean, default false) - Completion status
     - `note_id` (uuid, foreign key) - Reference to the parent note
     - `created_at` (timestamptz) - Timestamp when action item was created
     - `updated_at` (timestamptz) - Timestamp when action item was last updated

  4. **note_tags**
     - `note_id` (uuid, foreign key) - Reference to note
     - `tag_id` (uuid, foreign key) - Reference to tag
     - Primary key is combination of (note_id, tag_id)
     - Junction table for many-to-many relationship

  ## Security
  - Row Level Security (RLS) enabled on all tables
  - Public access policies for demo purposes (can be restricted later)

  ## Indexes
  - Indexes on foreign keys for better query performance
  - Index on tag names for faster lookups
*/

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create action_items table
CREATE TABLE IF NOT EXISTS action_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  description text NOT NULL,
  completed boolean DEFAULT false,
  note_id uuid REFERENCES notes(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create note_tags junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS note_tags (
  note_id uuid REFERENCES notes(id) ON DELETE CASCADE,
  tag_id uuid REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id);
CREATE INDEX IF NOT EXISTS idx_action_items_completed ON action_items(completed);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id);
CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id);

-- Enable Row Level Security
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_tags ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (demo purposes)
-- In production, these should be restricted to authenticated users

CREATE POLICY "Allow public read access to notes"
  ON notes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to notes"
  ON notes FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update access to notes"
  ON notes FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete access to notes"
  ON notes FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public read access to tags"
  ON tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to tags"
  ON tags FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update access to tags"
  ON tags FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete access to tags"
  ON tags FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public read access to action_items"
  ON action_items FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to action_items"
  ON action_items FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update access to action_items"
  ON action_items FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete access to action_items"
  ON action_items FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public read access to note_tags"
  ON note_tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert access to note_tags"
  ON note_tags FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public delete access to note_tags"
  ON note_tags FOR DELETE
  TO anon, authenticated
  USING (true);