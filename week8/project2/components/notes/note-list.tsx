"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Trash2, CreditCard as Edit, Search, Tag } from 'lucide-react';
import { NoteWithTags } from '@/lib/supabase';
import { NoteEditDialog } from './note-edit-dialog';

interface NoteListProps {
  refresh: number;
}

export function NoteList({ refresh }: NoteListProps) {
  const [notes, setNotes] = useState<NoteWithTags[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingNote, setEditingNote] = useState<NoteWithTags | null>(null);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const url = search
        ? `/api/notes?search=${encodeURIComponent(search)}`
        : '/api/notes';
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setNotes(data);
      }
    } catch (error) {
      console.error('Failed to fetch notes:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [refresh, search]);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
      const response = await fetch(`/api/notes/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchNotes();
      }
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-slate-800">My Notes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-5 w-5" />
            <Input
              placeholder="Search notes by title or content..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 bg-white border-slate-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="text-center text-slate-600">Loading notes...</div>
      ) : notes.length === 0 ? (
        <Card className="bg-white border-slate-200">
          <CardContent className="pt-6 text-center text-slate-500">
            No notes found. Create your first note above!
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {notes.map((note) => (
            <Card key={note.id} className="bg-white border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-xl font-bold text-slate-800 mb-2">
                      {note.title}
                    </CardTitle>
                    {note.tags && note.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2">
                        {note.tags.map((tag) => (
                          <Badge
                            key={tag.id}
                            variant="secondary"
                            className="bg-blue-100 text-blue-700 hover:bg-blue-200"
                          >
                            <Tag className="h-3 w-3 mr-1" />
                            {tag.name}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => setEditingNote(note)}
                      className="hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDelete(note.id)}
                      className="hover:bg-red-50 hover:text-red-600 hover:border-red-300"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-slate-700 whitespace-pre-wrap">{note.content}</p>
              </CardContent>
              <CardFooter className="text-sm text-slate-500">
                Created: {formatDate(note.created_at)} • Updated: {formatDate(note.updated_at)}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {editingNote && (
        <NoteEditDialog
          note={editingNote}
          onClose={() => setEditingNote(null)}
          onSuccess={() => {
            setEditingNote(null);
            fetchNotes();
          }}
        />
      )}
    </div>
  );
}
