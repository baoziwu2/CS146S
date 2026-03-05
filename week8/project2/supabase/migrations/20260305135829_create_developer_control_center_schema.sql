/*
  # Developer Control Center Schema

  ## Overview
  Creates the complete database schema for the Developer Control Center application,
  including tables for notes, tags, action items, and their relationships.

  ## New Tables
  
  ### 1. `notes`
  - `id` (uuid, primary key) - Unique identifier for each note
  - `title` (text, not null) - Title of the note
  - `content` (text, not null) - Main content of the note
  - `created_at` (timestamptz) - When the note was created
  - `updated_at` (timestamptz) - When the note was last updated
  
  ### 2. `tags`
  - `id` (uuid, primary key) - Unique identifier for each tag
  - `name` (text, unique, not null) - Tag name (e.g., "python", "fasthtml")
  - `created_at` (timestamptz) - When the tag was created
  
  ### 3. `action_items`
  - `id` (uuid, primary key) - Unique identifier for each action item
  - `description` (text, not null) - Description of the action item
  - `completed` (boolean, default false) - Completion status
  - `note_id` (uuid, nullable) - Reference to associated note (if auto-extracted)
  - `created_at` (timestamptz) - When the item was created
  - `updated_at` (timestamptz) - When the item was last updated
  
  ### 4. `note_tags` (Junction Table)
  - `note_id` (uuid, foreign key) - Reference to note
  - `tag_id` (uuid, foreign key) - Reference to tag
  - `created_at` (timestamptz) - When the association was created
  - Primary key: (note_id, tag_id)

  ## Security
  - Enable RLS on all tables
  - Add policies for public access (for demo purposes)
  
  ## Notes
  - All tables use UUID primary keys
  - Timestamps are automatically set using defaults
  - Foreign key constraints ensure referential integrity
  - Cascade deletes are configured for related data
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

-- Create note_tags junction table
CREATE TABLE IF NOT EXISTS note_tags (
  note_id uuid REFERENCES notes(id) ON DELETE CASCADE,
  tag_id uuid REFERENCES tags(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (note_id, tag_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id);
CREATE INDEX IF NOT EXISTS idx_action_items_completed ON action_items(completed);
CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id);
CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- Enable Row Level Security
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_tags ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (demo application)
CREATE POLICY "Allow public read access to notes"
  ON notes FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to notes"
  ON notes FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to notes"
  ON notes FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete to notes"
  ON notes FOR DELETE
  USING (true);

CREATE POLICY "Allow public read access to tags"
  ON tags FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to tags"
  ON tags FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to tags"
  ON tags FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete to tags"
  ON tags FOR DELETE
  USING (true);

CREATE POLICY "Allow public read access to action_items"
  ON action_items FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to action_items"
  ON action_items FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public update to action_items"
  ON action_items FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete to action_items"
  ON action_items FOR DELETE
  USING (true);

CREATE POLICY "Allow public read access to note_tags"
  ON note_tags FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert to note_tags"
  ON note_tags FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public delete to note_tags"
  ON note_tags FOR DELETE
  USING (true);
