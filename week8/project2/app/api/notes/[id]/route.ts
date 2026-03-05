import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { extractTags, extractActionItems } from '@/lib/extraction';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { data: note, error } = await supabase
      .from('notes')
      .select(`
        *,
        tags:note_tags(tag:tags(*))
      `)
      .eq('id', params.id)
      .maybeSingle();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    if (!note) {
      return NextResponse.json({ error: 'Note not found' }, { status: 404 });
    }

    const noteWithTags = {
      ...note,
      tags: note.tags?.map((t: any) => t.tag).filter(Boolean) || []
    };

    return NextResponse.json(noteWithTags);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch note' }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const { title, content } = body;

    if (!title || !content) {
      return NextResponse.json({ error: 'Title and content are required' }, { status: 400 });
    }

    const { data: note, error: noteError } = await supabase
      .from('notes')
      .update({ title, content, updated_at: new Date().toISOString() })
      .eq('id', params.id)
      .select()
      .single();

    if (noteError) {
      return NextResponse.json({ error: noteError.message }, { status: 500 });
    }

    await supabase.from('note_tags').delete().eq('note_id', params.id);

    const tagNames = extractTags(content);
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

    await supabase.from('action_items').delete().eq('note_id', params.id);

    const actionItemDescriptions = extractActionItems(content);
    for (const description of actionItemDescriptions) {
      await supabase
        .from('action_items')
        .insert({ description, note_id: note.id });
    }

    return NextResponse.json({ ...note, tags });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update note' }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { error } = await supabase
      .from('notes')
      .delete()
      .eq('id', params.id);

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ message: 'Note deleted successfully' });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to delete note' }, { status: 500 });
  }
}
