"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface NoteFormProps {
  onSuccess: () => void;
}

export function NoteForm({ onSuccess }: NoteFormProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });

      if (response.ok) {
        setTitle('');
        setContent('');
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to create note:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-slate-800">Create New Note</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              placeholder="Note Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="bg-white border-slate-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <Textarea
              placeholder="Note content... Use #tags for tags and add action items like:&#10;- [ ] Task with checkbox&#10;TODO: Another task&#10;Need to do something!&#10;Must complete this task"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              rows={8}
              className="bg-white border-slate-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold"
          >
            {loading ? 'Creating...' : 'Create Note'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
