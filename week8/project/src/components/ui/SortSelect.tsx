import { ArrowUpDown } from 'lucide-react';

interface SortOption {
  value: string;
  label: string;
}

interface SortSelectProps {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  options: SortOption[];
  onSortByChange: (value: string) => void;
  onSortOrderChange: (order: 'asc' | 'desc') => void;
}

export default function SortSelect({
  sortBy,
  sortOrder,
  options,
  onSortByChange,
  onSortOrderChange,
}: SortSelectProps) {
  return (
    <div className="flex items-center gap-2">
      <ArrowUpDown size={14} className="text-gray-400" />
      <select
        value={sortBy}
        onChange={(e) => onSortByChange(e.target.value)}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <select
        value={sortOrder}
        onChange={(e) => onSortOrderChange(e.target.value as 'asc' | 'desc')}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="desc">Newest first</option>
        <option value="asc">Oldest first</option>
      </select>
    </div>
  );
}
