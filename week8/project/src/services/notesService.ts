import { supabase } from '../lib/supabaseClient';
import { extractHashtags, extractActionItems } from '../lib/extractors';
import { upsertTag } from './tagsService';
import type { Note, NoteListParams, PaginatedResult } from '../types';

async function syncNoteTags(noteId: string, content: string): Promise<void> {
  const tagNames = extractHashtags(content);

  await supabase.from('note_tags').delete().eq('note_id', noteId);

  if (tagNames.length === 0) return;

  const tags = await Promise.all(tagNames.map((name) => upsertTag(name)));
  const rows = tags.map((tag) => ({ note_id: noteId, tag_id: tag.id }));
  const { error } = await supabase.from('note_tags').insert(rows);
  if (error) throw new Error(error.message);
}

async function extractAndCreateActionItems(content: string): Promise<void> {
  const descriptions = extractActionItems(content);
  if (descriptions.length === 0) return;

  for (const description of descriptions) {
    const { data: existing } = await supabase
      .from('action_items')
      .select('id')
      .eq('description', description)
      .maybeSingle();

    if (!existing) {
      await supabase.from('action_items').insert({ description });
    }
  }
}

function mapRow(row: any): Note {
  return {
    id: row.id,
    title: row.title,
    content: row.content,
    created_at: row.created_at,
    updated_at: row.updated_at,
    tags: (row.note_tags ?? []).map((nt: any) => nt.tags).filter(Boolean),
  };
}

export async function listNotes(params: NoteListParams = {}): Promise<PaginatedResult<Note>> {
  const {
    search = '',
    tagId,
    page = 1,
    pageSize = 10,
    sortBy = 'updated_at',
    sortOrder = 'desc',
  } = params;

  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;

  if (tagId) {
    const { data: taggedNoteIds } = await supabase
      .from('note_tags')
      .select('note_id')
      .eq('tag_id', tagId);

    const ids = (taggedNoteIds ?? []).map((r: any) => r.note_id as string);
    if (ids.length === 0) {
      return { data: [], total: 0, page, pageSize, totalPages: 0 };
    }

    let query = supabase
      .from('notes')
      .select('*, note_tags(tag_id, tags(id, name, created_at, updated_at))', { count: 'exact' })
      .in('id', ids);

    if (search.trim()) {
      query = query.or(`title.ilike.%${search.trim()}%,content.ilike.%${search.trim()}%`);
    }

    query = query.order(sortBy, { ascending: sortOrder === 'asc' }).range(from, to);

    const { data, error, count } = await query;
    if (error) throw new Error(error.message);

    const total = count ?? 0;
    return {
      data: (data ?? []).map(mapRow),
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize),
    };
  }

  let query = supabase
    .from('notes')
    .select('*, note_tags(tag_id, tags(id, name, created_at, updated_at))', { count: 'exact' });

  if (search.trim()) {
    query = query.or(`title.ilike.%${search.trim()}%,content.ilike.%${search.trim()}%`);
  }

  query = query.order(sortBy, { ascending: sortOrder === 'asc' }).range(from, to);

  const { data, error, count } = await query;
  if (error) throw new Error(error.message);

  const total = count ?? 0;
  return {
    data: (data ?? []).map(mapRow),
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize),
  };
}

export async function getNoteById(id: string): Promise<Note> {
  const { data, error } = await supabase
    .from('notes')
    .select('*, note_tags(tag_id, tags(id, name, created_at, updated_at))')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(error.message);
  if (!data) throw new Error('Note not found');
  return mapRow(data);
}

export async function createNote(title: string, content: string): Promise<Note> {
  if (!title.trim()) throw new Error('Title is required');

  const { data, error } = await supabase
    .from('notes')
    .insert({ title: title.trim(), content: content.trim() })
    .select()
    .single();

  if (error) throw new Error(error.message);

  await syncNoteTags(data.id, content);
  await extractAndCreateActionItems(content);

  return getNoteById(data.id);
}

export async function updateNote(
  id: string,
  fields: Partial<{ title: string; content: string }>
): Promise<Note> {
  if (fields.title !== undefined && !fields.title.trim()) {
    throw new Error('Title cannot be empty');
  }

  const updates: Record<string, string> = {};
  if (fields.title !== undefined) updates.title = fields.title.trim();
  if (fields.content !== undefined) updates.content = fields.content.trim();

  const { error } = await supabase.from('notes').update(updates).eq('id', id);
  if (error) throw new Error(error.message);

  if (fields.content !== undefined) {
    await syncNoteTags(id, fields.content);
    await extractAndCreateActionItems(fields.content);
  }

  return getNoteById(id);
}

export async function deleteNote(id: string): Promise<void> {
  const { error } = await supabase.from('notes').delete().eq('id', id);
  if (error) throw new Error(error.message);
}
