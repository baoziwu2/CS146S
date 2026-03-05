import { supabase } from '../lib/supabaseClient';
import type { ActionItem, ActionItemListParams, PaginatedResult } from '../types';

export async function listActionItems(
  params: ActionItemListParams = {}
): Promise<PaginatedResult<ActionItem>> {
  const {
    completedOnly = false,
    page = 1,
    pageSize = 10,
    sortBy = 'updated_at',
    sortOrder = 'desc',
  } = params;

  const from = (page - 1) * pageSize;
  const to = from + pageSize - 1;

  let query = supabase
    .from('action_items')
    .select('*', { count: 'exact' });

  if (completedOnly) {
    query = query.eq('completed', true);
  }

  query = query.order(sortBy, { ascending: sortOrder === 'asc' }).range(from, to);

  const { data, error, count } = await query;

  if (error) throw new Error(error.message);

  const total = count ?? 0;
  return {
    data: data ?? [],
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize),
  };
}

export async function createActionItem(description: string): Promise<ActionItem> {
  if (!description.trim()) throw new Error('Description is required');

  const { data, error } = await supabase
    .from('action_items')
    .insert({ description: description.trim() })
    .select()
    .single();

  if (error) throw new Error(error.message);
  return data;
}

export async function toggleActionItem(id: string, completed: boolean): Promise<ActionItem> {
  const { data, error } = await supabase
    .from('action_items')
    .update({ completed })
    .eq('id', id)
    .select()
    .single();

  if (error) throw new Error(error.message);
  return data;
}

export async function deleteActionItem(id: string): Promise<void> {
  const { error } = await supabase.from('action_items').delete().eq('id', id);
  if (error) throw new Error(error.message);
}
