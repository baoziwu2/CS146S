import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { extractTags, extractActionItems } from '@/lib/extraction';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const search = searchParams.get('search');

    let query = supabase
      .from('notes')
      .select(`
        *,
        tags:note_tags(tag:tags(*))
      `)
      .order('created_at', { ascending: false });

    if (search) {
      query = query.or(`title.ilike.%${search}%,content.ilike.%${search}%`);
    }

    const { data, error } = await query;

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const notesWithTags = data.map((note: any) => ({
      ...note,
      tags: note.tags?.map((t: any) => t.tag).filter(Boolean) || []
    }));

    return NextResponse.json(notesWithTags);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch notes' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content } = body;

    if (!title || !content) {
      return NextResponse.json({ error: 'Title and content are required' }, { status: 400 });
    }

    const { data: note, error: noteError } = await supabase
      .from('notes')
      .insert({ title, content })
      .select()
      .single();

    if (noteError) {
      return NextResponse.json({ error: noteError.message }, { status: 500 });
    }

    const tagNames = extractTags(content);
    const actionItemDescriptions = extractActionItems(content);

    const tags = [];
    for (const tagName of tagNames) {
      const { data: existingTag } = await supabase
        .from('tags')
        .select()
        .eq('name', tagName)
        .maybeSingle();

      let tag = existingTag;
      if (!tag) {
        const { data: newTag } = await supabase
          .from('tags')
          .insert({ name: tagName })
          .select()
          .single();
        tag = newTag;
      }

      if (tag) {
        await supabase
          .from('note_tags')
          .insert({ note_id: note.id, tag_id: tag.id });
        tags.push(tag);
      }
    }

    for (const description of actionItemDescriptions) {
      await supabase
        .from('action_items')
        .insert({ description, note_id: note.id });
    }

    return NextResponse.json({ ...note, tags }, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create note' }, { status: 500 });
  }
}
