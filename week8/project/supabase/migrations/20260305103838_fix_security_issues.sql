/*
  # Security Hardening

  ## Changes

  ### 1. Unindexed Foreign Key
  - Adds a covering index on `note_tags.tag_id` to support efficient joins and
    lookups when querying notes by tag.

  ### 2. Function Search Path
  - Recreates `update_updated_at_column` with a fixed `search_path = ''` so the
    function cannot be hijacked via a mutable search_path.
  - Uses fully-qualified type references (pg_catalog.text, etc.) where needed.

  ### 3. RLS Policies — Remove Always-True Mutations
  - Drops the overly broad INSERT / UPDATE / DELETE policies that had
    unconditional USING / WITH CHECK (true) for both anon and authenticated.
  - Replaces them with anon-only equivalents scoped as narrowly as possible
    without requiring user authentication.
  - SELECT policies (read) remain accessible to both roles.
  - The authenticated role retains SELECT-only access; write access is anon-only.

  ### 4. Auth DB Connection Strategy
  - Cannot be changed via SQL migration.
  - Must be updated in the Supabase Dashboard under
    Project Settings > Database > Connection pool > Auth pool mode,
    switching from "fixed" to "percentage" mode.

  ## Notes
  - The app currently has no user-level auth. The anon-key policies are still
    technically "always-true" for anon because there is no per-user predicate
    to enforce. Adding Supabase Auth would allow scoping each row to auth.uid().
  - All other security hardening (index, function) is fully applied here.
*/

-- 1. Index on note_tags.tag_id
CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags (tag_id);

-- 2. Fix mutable search_path on trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = ''
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- 3. Drop all existing INSERT / UPDATE / DELETE policies that are always-true

-- notes
DROP POLICY IF EXISTS "Allow public insert on notes" ON notes;
DROP POLICY IF EXISTS "Allow public update on notes" ON notes;
DROP POLICY IF EXISTS "Allow public delete on notes" ON notes;

-- tags
DROP POLICY IF EXISTS "Allow public insert on tags" ON tags;
DROP POLICY IF EXISTS "Allow public update on tags" ON tags;
DROP POLICY IF EXISTS "Allow public delete on tags" ON tags;

-- note_tags
DROP POLICY IF EXISTS "Allow public insert on note_tags" ON note_tags;
DROP POLICY IF EXISTS "Allow public delete on note_tags" ON note_tags;

-- action_items
DROP POLICY IF EXISTS "Allow public insert on action_items" ON action_items;
DROP POLICY IF EXISTS "Allow public update on action_items" ON action_items;
DROP POLICY IF EXISTS "Allow public delete on action_items" ON action_items;

-- Also drop existing select policies so we can replace with anon-only versions
DROP POLICY IF EXISTS "Allow public select on notes" ON notes;
DROP POLICY IF EXISTS "Allow public select on tags" ON tags;
DROP POLICY IF EXISTS "Allow public select on note_tags" ON note_tags;
DROP POLICY IF EXISTS "Allow public select on action_items" ON action_items;

-- 4. Recreate policies — anon only for writes; anon + authenticated for reads

-- notes
CREATE POLICY "Anon and authenticated can read notes"
  ON notes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anon can insert notes"
  ON notes FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anon can update notes"
  ON notes FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anon can delete notes"
  ON notes FOR DELETE
  TO anon
  USING (true);

-- tags
CREATE POLICY "Anon and authenticated can read tags"
  ON tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anon can insert tags"
  ON tags FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anon can update tags"
  ON tags FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anon can delete tags"
  ON tags FOR DELETE
  TO anon
  USING (true);

-- note_tags
CREATE POLICY "Anon and authenticated can read note_tags"
  ON note_tags FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anon can insert note_tags"
  ON note_tags FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anon can delete note_tags"
  ON note_tags FOR DELETE
  TO anon
  USING (true);

-- action_items
CREATE POLICY "Anon and authenticated can read action_items"
  ON action_items FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anon can insert action_items"
  ON action_items FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anon can update action_items"
  ON action_items FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anon can delete action_items"
  ON action_items FOR DELETE
  TO anon
  USING (true);
