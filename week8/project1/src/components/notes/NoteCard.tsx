import { Pencil, Trash2, Clock } from 'lucide-react';
import type { Note } from '../../types';

interface NoteCardProps {
  note: Note;
  onEdit: (note: Note) => void;
  onDelete: (note: Note) => void;
}

function formatDate(dateStr: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateStr));
}

function tagColor(name: string) {
  const colors = [
    'bg-blue-100 text-blue-700',
    'bg-emerald-100 text-emerald-700',
    'bg-amber-100 text-amber-700',
    'bg-sky-100 text-sky-700',
    'bg-rose-100 text-rose-700',
    'bg-teal-100 text-teal-700',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}

export default function NoteCard({ note, onEdit, onDelete }: NoteCardProps) {
  const preview = note.content.length > 120 ? note.content.slice(0, 120) + '…' : note.content;

  return (
    <div className="group bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition-all duration-150">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate mb-1">{note.title}</h3>
          {preview && (
            <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 mb-2">{preview}</p>
          )}
          {note.tags && note.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {note.tags.map((tag) => (
                <span
                  key={tag.id}
                  className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${tagColor(tag.name)}`}
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}
          <div className="flex items-center gap-1 text-[10px] text-gray-400">
            <Clock size={10} />
            <span>{formatDate(note.updated_at)}</span>
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(note)}
            className="p-1.5 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-colors"
            title="Edit note"
          >
            <Pencil size={13} />
          </button>
          <button
            onClick={() => onDelete(note)}
            className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600 transition-colors"
            title="Delete note"
          >
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}
