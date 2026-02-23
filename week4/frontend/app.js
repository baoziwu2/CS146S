async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes(q = '') {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = q ? `/notes/search/?q=${encodeURIComponent(q)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const title = prompt('New title:', n.title);
      if (title === null) return;
      const content = prompt('New content:', n.content);
      if (content === null) return;
      await fetchJSON(`/notes/${n.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      loadNotes(q);
    };

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      await fetch(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes(q);
    };

    li.appendChild(editBtn);
    li.appendChild(delBtn);
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('search-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const q = document.getElementById('search-query').value.trim();
    loadNotes(q);
  });

  document.getElementById('search-form').addEventListener('reset', () => {
    loadNotes();
  });

  loadNotes();
  loadActions();
});
