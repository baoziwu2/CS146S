import { CheckCircle2, Circle, Trash2, Clock } from 'lucide-react';
import type { ActionItem } from '../../types';

interface ActionItemRowProps {
  item: ActionItem;
  onToggle: (item: ActionItem) => void;
  onDelete: (item: ActionItem) => void;
  toggling: boolean;
}

function formatDate(dateStr: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(dateStr));
}

export default function ActionItemRow({ item, onToggle, onDelete, toggling }: ActionItemRowProps) {
  return (
    <div
      className={`group flex items-start gap-3 p-3.5 rounded-xl border transition-all duration-150 ${
        item.completed
          ? 'bg-gray-50 border-gray-200'
          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-sm'
      }`}
    >
      <button
        onClick={() => onToggle(item)}
        disabled={toggling}
        className={`mt-0.5 flex-shrink-0 transition-colors disabled:opacity-50 ${
          item.completed ? 'text-emerald-500 hover:text-emerald-600' : 'text-gray-300 hover:text-blue-500'
        }`}
        title={item.completed ? 'Reopen' : 'Mark complete'}
      >
        {item.completed ? <CheckCircle2 size={18} /> : <Circle size={18} />}
      </button>

      <div className="flex-1 min-w-0">
        <p
          className={`text-sm leading-snug ${
            item.completed ? 'line-through text-gray-400' : 'text-gray-800'
          }`}
        >
          {item.description}
        </p>
        <div className="flex items-center gap-2 mt-1.5">
          {item.completed && (
            <span className="text-[10px] font-medium bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">
              Completed
            </span>
          )}
          <div className="flex items-center gap-1 text-[10px] text-gray-400">
            <Clock size={10} />
            <span>{formatDate(item.updated_at)}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
        <button
          onClick={() => onToggle(item)}
          disabled={toggling}
          className={`text-[10px] font-medium px-2.5 py-1 rounded-lg border transition-colors disabled:opacity-50 ${
            item.completed
              ? 'border-gray-200 text-gray-500 hover:bg-gray-100'
              : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'
          }`}
        >
          {item.completed ? 'Reopen' : 'Complete'}
        </button>
        <button
          onClick={() => onDelete(item)}
          className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600 transition-colors"
          title="Delete"
        >
          <Trash2 size={13} />
        </button>
      </div>
    </div>
  );
}
