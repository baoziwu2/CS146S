"""
Data models and database operations.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from db import supabase
from services.extract import extract_tags, extract_action_items


class Note:
    """Note model with CRUD operations."""

    @staticmethod
    def create(title: str, content: str) -> Dict[str, Any]:
        """Create a new note and auto-extract tags and action items."""
        result = supabase.table('notes').insert({
            'title': title,
            'content': content
        }).execute()

        note = result.data[0]
        note_id = note['id']

        tag_names = extract_tags(content)
        for tag_name in tag_names:
            tag = Tag.get_or_create(tag_name)
            supabase.table('note_tags').insert({
                'note_id': note_id,
                'tag_id': tag['id']
            }).execute()

        action_item_texts = extract_action_items(content)
        for item_text in action_item_texts:
            ActionItem.create(item_text, note_id)

        return note

    @staticmethod
    def get_all(search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all notes, optionally filtered by search keyword."""
        query = supabase.table('notes').select('*').order('created_at', desc=True)

        if search:
            query = query.or_(f'title.ilike.%{search}%,content.ilike.%{search}%')

        result = query.execute()
        notes = result.data

        for note in notes:
            note['tags'] = Note.get_tags(note['id'])

        return notes

    @staticmethod
    def get_by_id(note_id: str) -> Optional[Dict[str, Any]]:
        """Get a single note by ID."""
        result = supabase.table('notes').select('*').eq('id', note_id).maybeSingle().execute()
        if result.data:
            result.data['tags'] = Note.get_tags(note_id)
        return result.data

    @staticmethod
    def update(note_id: str, title: str, content: str) -> Dict[str, Any]:
        """Update a note and re-extract tags and action items."""
        result = supabase.table('notes').update({
            'title': title,
            'content': content,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', note_id).execute()

        supabase.table('note_tags').delete().eq('note_id', note_id).execute()

        tag_names = extract_tags(content)
        for tag_name in tag_names:
            tag = Tag.get_or_create(tag_name)
            supabase.table('note_tags').insert({
                'note_id': note_id,
                'tag_id': tag['id']
            }).execute()

        supabase.table('action_items').delete().eq('note_id', note_id).execute()

        action_item_texts = extract_action_items(content)
        for item_text in action_item_texts:
            ActionItem.create(item_text, note_id)

        return result.data[0] if result.data else None

    @staticmethod
    def delete(note_id: str) -> None:
        """Delete a note."""
        supabase.table('notes').delete().eq('id', note_id).execute()

    @staticmethod
    def get_tags(note_id: str) -> List[Dict[str, Any]]:
        """Get all tags associated with a note."""
        result = supabase.table('note_tags').select('tag_id, tags(id, name)').eq('note_id', note_id).execute()
        return [item['tags'] for item in result.data]


class Tag:
    """Tag model with CRUD operations."""

    @staticmethod
    def get_or_create(name: str) -> Dict[str, Any]:
        """Get existing tag or create new one."""
        result = supabase.table('tags').select('*').eq('name', name).maybeSingle().execute()

        if result.data:
            return result.data
        else:
            result = supabase.table('tags').insert({'name': name}).execute()
            return result.data[0]

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all tags."""
        result = supabase.table('tags').select('*').order('name').execute()
        return result.data


class ActionItem:
    """Action item model with CRUD operations."""

    @staticmethod
    def create(description: str, note_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new action item."""
        result = supabase.table('action_items').insert({
            'description': description,
            'note_id': note_id
        }).execute()
        return result.data[0]

    @staticmethod
    def get_all(completed_only: bool = False) -> List[Dict[str, Any]]:
        """Get all action items, optionally filtered by completion status."""
        query = supabase.table('action_items').select('*').order('created_at', desc=True)

        if completed_only:
            query = query.eq('completed', True)

        result = query.execute()
        return result.data

    @staticmethod
    def get_by_id(item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single action item by ID."""
        result = supabase.table('action_items').select('*').eq('id', item_id).maybeSingle().execute()
        return result.data

    @staticmethod
    def toggle_completed(item_id: str) -> Dict[str, Any]:
        """Toggle the completed status of an action item."""
        item = ActionItem.get_by_id(item_id)
        if not item:
            return None

        result = supabase.table('action_items').update({
            'completed': not item['completed'],
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', item_id).execute()

        return result.data[0] if result.data else None

    @staticmethod
    def delete(item_id: str) -> None:
        """Delete an action item."""
        supabase.table('action_items').delete().eq('id', item_id).execute()
