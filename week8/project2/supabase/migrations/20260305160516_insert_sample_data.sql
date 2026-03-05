/*
  # Insert Sample Data for Developer Control Center

  ## Overview
  This migration populates the database with sample data for testing and demonstration purposes.

  ## Data Inserted

  1. **Notes** - 5 sample notes with various content including:
     - Tags (hashtags like #python, #javascript, #react)
     - Action items in various formats (checkboxes, TODO:, Need to, etc.)

  2. **Tags** - Automatically created from note content:
     - python, javascript, react, nextjs, typescript, api, database, ui

  3. **Action Items** - Automatically extracted from note content:
     - Mix of completed and pending items
     - Various formats (checkboxes, imperative verbs, TODO/FIXME prefixes)

  4. **Note-Tag Relationships** - Junction table entries linking notes to their tags

  ## Notes
  - All timestamps use the current time
  - Sample data demonstrates the auto-extraction features
  - Mix of completed and pending action items for testing filtering
*/

-- Insert sample notes with various tags and action items
DO $$
DECLARE
  note1_id uuid;
  note2_id uuid;
  note3_id uuid;
  note4_id uuid;
  note5_id uuid;
  tag_python_id uuid;
  tag_javascript_id uuid;
  tag_react_id uuid;
  tag_nextjs_id uuid;
  tag_typescript_id uuid;
  tag_api_id uuid;
  tag_database_id uuid;
  tag_ui_id uuid;
BEGIN
  -- Create tags
  INSERT INTO tags (name) VALUES ('python') RETURNING id INTO tag_python_id;
  INSERT INTO tags (name) VALUES ('javascript') RETURNING id INTO tag_javascript_id;
  INSERT INTO tags (name) VALUES ('react') RETURNING id INTO tag_react_id;
  INSERT INTO tags (name) VALUES ('nextjs') RETURNING id INTO tag_nextjs_id;
  INSERT INTO tags (name) VALUES ('typescript') RETURNING id INTO tag_typescript_id;
  INSERT INTO tags (name) VALUES ('api') RETURNING id INTO tag_api_id;
  INSERT INTO tags (name) VALUES ('database') RETURNING id INTO tag_database_id;
  INSERT INTO tags (name) VALUES ('ui') RETURNING id INTO tag_ui_id;

  -- Note 1: Python API Development
  INSERT INTO notes (title, content) VALUES (
    'Python API Development Notes',
    'Working on a new #python #api backend service.

- [ ] Set up FastAPI project structure
- [ ] Configure database connection
TODO: Implement user authentication endpoints
Need to add input validation for all endpoints!

The API should handle CRUD operations efficiently. Must ensure proper error handling throughout.'
  ) RETURNING id INTO note1_id;

  INSERT INTO note_tags (note_id, tag_id) VALUES (note1_id, tag_python_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note1_id, tag_api_id);

  INSERT INTO action_items (description, note_id, completed) VALUES
    ('Set up FastAPI project structure', note1_id, true),
    ('Configure database connection', note1_id, false),
    ('Implement user authentication endpoints', note1_id, false),
    ('add input validation for all endpoints', note1_id, false),
    ('ensure proper error handling throughout.', note1_id, false);

  -- Note 2: React Component Library
  INSERT INTO notes (title, content) VALUES (
    'Building a React Component Library',
    'Starting a new component library with #react and #typescript.

- [ ] Create button component variants
- [ ] Design form input components
FIXME: Fix accessibility issues in modal component
Please review the color contrast ratios
Should add unit tests for all components

This will be used across multiple projects. #ui #nextjs'
  ) RETURNING id INTO note2_id;

  INSERT INTO note_tags (note_id, tag_id) VALUES (note2_id, tag_react_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note2_id, tag_typescript_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note2_id, tag_ui_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note2_id, tag_nextjs_id);

  INSERT INTO action_items (description, note_id, completed) VALUES
    ('Create button component variants', note2_id, false),
    ('Design form input components', note2_id, false),
    ('Fix accessibility issues in modal component', note2_id, false),
    ('review the color contrast ratios', note2_id, false),
    ('add unit tests for all components', note2_id, false);

  -- Note 3: Database Schema Design
  INSERT INTO notes (title, content) VALUES (
    'Database Schema Design for E-commerce',
    'Designing the #database schema for the new e-commerce platform.

- [x] Define user and authentication tables
- [x] Create product catalog schema
- [ ] Design order management tables
Action: Add indexes for frequently queried fields
Must optimize for read-heavy operations!

Consider implementing caching layer. #api'
  ) RETURNING id INTO note3_id;

  INSERT INTO note_tags (note_id, tag_id) VALUES (note3_id, tag_database_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note3_id, tag_api_id);

  INSERT INTO action_items (description, note_id, completed) VALUES
    ('Design order management tables', note3_id, false),
    ('Add indexes for frequently queried fields', note3_id, false),
    ('optimize for read-heavy operations', note3_id, false);

  -- Note 4: Next.js Migration Plan
  INSERT INTO notes (title, content) VALUES (
    'Migrating to Next.js 14',
    'Planning the migration from Next.js 13 to 14. #nextjs #react

- [ ] Update all dependencies
- [ ] Migrate to App Router
TODO: Convert pages to server components where possible
FIXME: Fix build errors in production
Need to test all routes thoroughly
Should implement proper loading states!

Follow up: Performance testing after migration'
  ) RETURNING id INTO note4_id;

  INSERT INTO note_tags (note_id, tag_id) VALUES (note4_id, tag_nextjs_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note4_id, tag_react_id);

  INSERT INTO action_items (description, note_id, completed) VALUES
    ('Update all dependencies', note4_id, false),
    ('Migrate to App Router', note4_id, false),
    ('Convert pages to server components where possible', note4_id, false),
    ('Fix build errors in production', note4_id, false),
    ('test all routes thoroughly', note4_id, false),
    ('implement proper loading states', note4_id, false),
    ('Performance testing after migration', note4_id, false);

  -- Note 5: TypeScript Best Practices
  INSERT INTO notes (title, content) VALUES (
    'TypeScript Best Practices',
    'Collecting #typescript best practices for the team.

- [x] Use strict mode in tsconfig
- [x] Define interfaces for all data structures
- [ ] Implement type guards for runtime validation
Must avoid using any type!
Please add JSDoc comments for complex types
Need to set up automated type checking in CI/CD

The codebase should be fully typed. #javascript'
  ) RETURNING id INTO note5_id;

  INSERT INTO note_tags (note_id, tag_id) VALUES (note5_id, tag_typescript_id);
  INSERT INTO note_tags (note_id, tag_id) VALUES (note5_id, tag_javascript_id);

  INSERT INTO action_items (description, note_id, completed) VALUES
    ('Implement type guards for runtime validation', note5_id, false),
    ('avoid using any type', note5_id, false),
    ('add JSDoc comments for complex types', note5_id, false),
    ('set up automated type checking in CI/CD', note5_id, false);

END $$;
