"use client";

import { useState } from 'react';
import { NoteForm } from '@/components/notes/note-form';
import { NoteList } from '@/components/notes/note-list';
import { ActionItemForm } from '@/components/action-items/action-item-form';
import { ActionItemList } from '@/components/action-items/action-item-list';
import { Separator } from '@/components/ui/separator';
import { BookOpen, SquareCheck as CheckSquare } from 'lucide-react';

export default function Home() {
  const [noteRefresh, setNoteRefresh] = useState(0);
  const [actionItemRefresh, setActionItemRefresh] = useState(0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 mb-3 bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
            Developer Control Center
          </h1>
          <p className="text-lg text-slate-600">
            Organize your notes, track tasks, and boost productivity
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="h-6 w-6 text-blue-600" />
              <h2 className="text-3xl font-bold text-slate-800">Notes</h2>
            </div>

            <NoteForm
              onSuccess={() => {
                setNoteRefresh(prev => prev + 1);
                setActionItemRefresh(prev => prev + 1);
              }}
            />

            <NoteList refresh={noteRefresh} />
          </div>

          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <CheckSquare className="h-6 w-6 text-emerald-600" />
              <h2 className="text-3xl font-bold text-slate-800">Action Items</h2>
            </div>

            <ActionItemForm
              onSuccess={() => setActionItemRefresh(prev => prev + 1)}
            />

            <ActionItemList refresh={actionItemRefresh} />
          </div>
        </div>

        <footer className="mt-16 text-center text-slate-500 text-sm border-t border-slate-200 pt-8">
          <p>Developer Control Center - Manage your development workflow efficiently</p>
        </footer>
      </div>
    </div>
  );
}
