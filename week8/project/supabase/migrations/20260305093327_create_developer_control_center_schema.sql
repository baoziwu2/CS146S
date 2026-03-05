
/*
  # Developer Control Center - Initial Schema

  ## Summary
  Creates the core data models for the Developer Control Center application.

  ## New Tables

  ### 1. notes
  - id (uuid, primary key)
  - title (text, required)
  - content (text)
  - created_at (timestamptz, default now())
  - updated_at (timestamptz, default now())

  ### 2. tags
  - id (uuid, primary key)
  - name (text, unique, required)
  - created_at (timestamptz, default now())
  - updated_at (timestamptz, default now())

  ### 3. note_tags (junction table)
  - note_id (uuid, FK -> notes.id)
  - tag_id (uuid, FK -> tags.id)
  - PRIMARY KEY (note_id, tag_id)

  ### 4. action_items
  - id (uuid, primary key)
  - description (text, required)
  - completed (boolean, default false)
  - created_at (timestamptz, default now())
  - updated_at (timestamptz, default now())

  ## Security
  - RLS enabled on all tables
  - Policies allow authenticated users to manage their own data
  - Public read/write for now (anon key usage in frontend)

  ## Notes
  - updated_at is automatically maintained via triggers
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL DEFAULT '',
  content text NOT NULL DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS note_tags (
  note_id uuid NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  tag_id uuid NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE IF NOT EXISTS action_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  description text NOT NULL DEFAULT '',
  completed boolean NOT NULL DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select on notes"
  ON notes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert on notes"
  ON notes FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update on notes"
  ON notes FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete on notes"
  ON notes FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public select on tags"
  ON tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert on tags"
  ON tags FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update on tags"
  ON tags FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete on tags"
  ON tags FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public select on note_tags"
  ON note_tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert on note_tags"
  ON note_tags FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public delete on note_tags"
  ON note_tags FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public select on action_items"
  ON action_items FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert on action_items"
  ON action_items FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update on action_items"
  ON action_items FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete on action_items"
  ON action_items FOR DELETE
  TO anon, authenticated
  USING (true);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_notes_updated_at
  BEFORE UPDATE ON notes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at
  BEFORE UPDATE ON tags
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_items_updated_at
  BEFORE UPDATE ON action_items
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
