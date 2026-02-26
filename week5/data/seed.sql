CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS note_tags (
  note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE IF NOT EXISTS action_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0
);

-- Demo notes with #hashtags and - [ ] tasks
INSERT INTO notes (title, content) VALUES
  ('Welcome to the App', 'This is your starter note. #demo #welcome
- [ ] Explore the Notes section
- [ ] Try the tag filter bar above'),
  ('Python FastAPI Cheatsheet', '#python #fastapi #backend
Key patterns:
- [ ] Add dependency injection with Depends()
- [ ] Use Pydantic models for request/response
- [ ] Write tests with TestClient'),
  ('React + Vite Setup', '#react #frontend #vite
Getting started:
- [ ] Run npm install in frontend/
- [ ] Start dev server with npm run dev
Tip: Use forwardRef for imperative handles.'),
  ('Project Roadmap', '#planning #project
This week: finish tasks 5 and 6. #backend
- [ ] Tags many-to-many
- [ ] Extraction service
- [ ] Frontend tag chips'),
  ('SQL Notes', '#sql #database #backend
Useful SQLite tips:
- [ ] Use EXPLAIN QUERY PLAN to check indexes
- [ ] CASCADE deletes keep join tables clean');

-- Tags
INSERT INTO tags (name) VALUES
  ('demo'),
  ('welcome'),
  ('python'),
  ('fastapi'),
  ('backend'),
  ('react'),
  ('frontend'),
  ('vite'),
  ('planning'),
  ('project'),
  ('sql'),
  ('database');

-- Attach tags to notes
INSERT INTO note_tags (note_id, tag_id) VALUES
  (1, (SELECT id FROM tags WHERE name='demo')),
  (1, (SELECT id FROM tags WHERE name='welcome')),
  (2, (SELECT id FROM tags WHERE name='python')),
  (2, (SELECT id FROM tags WHERE name='fastapi')),
  (2, (SELECT id FROM tags WHERE name='backend')),
  (3, (SELECT id FROM tags WHERE name='react')),
  (3, (SELECT id FROM tags WHERE name='frontend')),
  (3, (SELECT id FROM tags WHERE name='vite')),
  (4, (SELECT id FROM tags WHERE name='planning')),
  (4, (SELECT id FROM tags WHERE name='project')),
  (4, (SELECT id FROM tags WHERE name='backend')),
  (5, (SELECT id FROM tags WHERE name='sql')),
  (5, (SELECT id FROM tags WHERE name='database')),
  (5, (SELECT id FROM tags WHERE name='backend'));

-- Action items
INSERT INTO action_items (description, completed) VALUES
  ('Explore the Notes section', 0),
  ('Try the tag filter bar', 0),
  ('Add dependency injection with Depends()', 0),
  ('Run npm install in frontend/', 0),
  ('Start dev server with npm run dev', 0),
  ('Tags many-to-many', 1),
  ('Extraction service', 1),
  ('Frontend tag chips', 0),
  ('Use EXPLAIN QUERY PLAN to check indexes', 0),
  ('CASCADE deletes keep join tables clean', 0);
