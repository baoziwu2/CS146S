import { supabase } from '../lib/supabaseClient';
import type { Tag } from '../types';

export async function listAllTags(): Promise<Tag[]> {
  const { data, error } = await supabase
    .from('tags')
    .select('*')
    .order('name', { ascending: true });

  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function upsertTag(name: string): Promise<Tag> {
  const normalized = name.toLowerCase().trim();

  const { data: existing } = await supabase
    .from('tags')
    .select('*')
    .eq('name', normalized)
    .maybeSingle();

  if (existing) return existing;

  const { data, error } = await supabase
    .from('tags')
    .insert({ name: normalized })
    .select()
    .single();

  if (error) throw new Error(error.message);
  return data;
}
