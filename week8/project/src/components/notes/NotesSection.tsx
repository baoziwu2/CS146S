import { useState, useEffect, useCallback } from 'react';
import { Search, Plus, FileText, Tag, X } from 'lucide-react';
import { listNotes, createNote, updateNote, deleteNote } from '../../services/notesService';
import { listAllTags } from '../../services/tagsService';
import type { Note, Tag as TagType, NoteListParams } from '../../types';
import NoteCard from './NoteCard';
import NoteForm from './NoteForm';
import Modal from '../ui/Modal';
import ConfirmDialog from '../ui/ConfirmDialog';
import Pagination from '../ui/Pagination';
import SortSelect from '../ui/SortSelect';
import EmptyState from '../ui/EmptyState';
import Button from '../ui/Button';

const PAGE_SIZE = 8;

const sortOptions = [
  { value: 'updated_at', label: 'Last updated' },
  { value: 'created_at', label: 'Date created' },
  { value: 'title', label: 'Title' },
];

const TAG_COLORS = [
  'bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-200',
  'bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200',
  'bg-amber-100 text-amber-700 border-amber-200 hover:bg-amber-200',
  'bg-sky-100 text-sky-700 border-sky-200 hover:bg-sky-200',
  'bg-rose-100 text-rose-700 border-rose-200 hover:bg-rose-200',
  'bg-teal-100 text-teal-700 border-teal-200 hover:bg-teal-200',
  'bg-orange-100 text-orange-700 border-orange-200 hover:bg-orange-200',
];

function tagColorClass(name: string) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return TAG_COLORS[Math.abs(hash) % TAG_COLORS.length];
}

function tagActiveClass(name: string) {
  const idx = (() => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return Math.abs(hash) % TAG_COLORS.length;
  })();
  const active = [
    'bg-blue-600 text-white border-blue-600',
    'bg-emerald-600 text-white border-emerald-600',
    'bg-amber-600 text-white border-amber-600',
    'bg-sky-600 text-white border-sky-600',
    'bg-rose-600 text-white border-rose-600',
    'bg-teal-600 text-white border-teal-600',
    'bg-orange-600 text-white border-orange-600',
  ];
  return active[idx];
}

export default function NotesSection() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [allTags, setAllTags] = useState<TagType[]>([]);
  const [selectedTagId, setSelectedTagId] = useState<string | undefined>(undefined);

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<NoteListParams['sortBy']>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const [createOpen, setCreateOpen] = useState(false);
  const [editNote, setEditNote] = useState<Note | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Note | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchTags = useCallback(async () => {
    try {
      const tags = await listAllTags();
      setAllTags(tags);
    } catch {}
  }, []);

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchNotes = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await listNotes({
        search: debouncedSearch,
        tagId: selectedTagId,
        page,
        pageSize: PAGE_SIZE,
        sortBy,
        sortOrder,
      });
      setNotes(result.data);
      setTotal(result.total);
      setTotalPages(result.totalPages);
    } catch (err: any) {
      setError(err.message ?? 'Failed to load notes');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, selectedTagId, page, sortBy, sortOrder]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleCreate = async (title: string, content: string) => {
    await createNote(title, content);
    setCreateOpen(false);
    setPage(1);
    await fetchTags();
    fetchNotes();
  };

  const handleUpdate = async (title: string, content: string) => {
    if (!editNote) return;
    await updateNote(editNote.id, { title, content });
    setEditNote(null);
    await fetchTags();
    fetchNotes();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await deleteNote(deleteTarget.id);
      setDeleteTarget(null);
      if (notes.length === 1 && page > 1) setPage((p) => p - 1);
      else fetchNotes();
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleTagClick = (tagId: string) => {
    setSelectedTagId((prev) => (prev === tagId ? undefined : tagId));
    setPage(1);
  };

  const handleSortByChange = (val: string) => {
    setSortBy(val as NoteListParams['sortBy']);
    setPage(1);
  };

  const handleSortOrderChange = (order: 'asc' | 'desc') => {
    setSortOrder(order);
    setPage(1);
  };

  const hasFilters = !!debouncedSearch || !!selectedTagId;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search notes by title or content..."
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center gap-3">
          <SortSelect
            sortBy={sortBy ?? 'updated_at'}
            sortOrder={sortOrder}
            options={sortOptions}
            onSortByChange={handleSortByChange}
            onSortOrderChange={handleSortOrderChange}
          />
          <Button onClick={() => setCreateOpen(true)} size="md">
            <Plus size={14} />
            New Note
          </Button>
        </div>
      </div>

      {allTags.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1 text-xs text-gray-500 flex-shrink-0">
            <Tag size={12} />
            <span className="font-medium">Filter by tag:</span>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            {allTags.map((tag) => {
              const isActive = selectedTagId === tag.id;
              return (
                <button
                  key={tag.id}
                  onClick={() => handleTagClick(tag.id)}
                  className={`
                    flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-full border
                    transition-all duration-100 select-none
                    ${isActive ? tagActiveClass(tag.name) : tagColorClass(tag.name)}
                  `}
                >
                  #{tag.name}
                  {isActive && <X size={10} className="ml-0.5" />}
                </button>
              );
            })}
            {selectedTagId && (
              <button
                onClick={() => { setSelectedTagId(undefined); setPage(1); }}
                className="text-[11px] font-medium text-gray-500 hover:text-gray-700 px-2 py-1 rounded-full hover:bg-gray-100 transition-colors"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-xl p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-full mb-1" />
              <div className="h-3 bg-gray-100 rounded w-4/5" />
            </div>
          ))}
        </div>
      ) : notes.length === 0 ? (
        <EmptyState
          icon={FileText}
          title={hasFilters ? 'No notes found' : 'No notes yet'}
          description={
            hasFilters
              ? 'No notes match the current filters. Try adjusting your search or tag selection.'
              : 'Create your first note to get started. Use #hashtags in content to auto-tag notes.'
          }
          action={
            !hasFilters ? (
              <Button onClick={() => setCreateOpen(true)} size="sm">
                <Plus size={12} />
                Create note
              </Button>
            ) : undefined
          }
        />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {notes.map((note) => (
              <NoteCard
                key={note.id}
                note={note}
                onEdit={setEditNote}
                onDelete={setDeleteTarget}
              />
            ))}
          </div>
          <Pagination
            page={page}
            totalPages={totalPages}
            total={total}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New Note">
        <NoteForm onSubmit={handleCreate} onCancel={() => setCreateOpen(false)} submitLabel="Create Note" />
      </Modal>

      <Modal open={editNote !== null} onClose={() => setEditNote(null)} title="Edit Note">
        {editNote && (
          <NoteForm
            initial={editNote}
            onSubmit={handleUpdate}
            onCancel={() => setEditNote(null)}
            submitLabel="Save Changes"
          />
        )}
      </Modal>

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Note"
        message={`Are you sure you want to delete "${deleteTarget?.title}"? This action cannot be undone.`}
        loading={deleteLoading}
      />
    </div>
  );
}
