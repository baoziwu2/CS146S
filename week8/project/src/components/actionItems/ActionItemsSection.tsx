import { useState, useEffect, useCallback } from 'react';
import { Plus, CheckSquare } from 'lucide-react';
import {
  listActionItems,
  createActionItem,
  toggleActionItem,
  deleteActionItem,
} from '../../services/actionItemsService';
import type { ActionItem, ActionItemListParams } from '../../types';
import ActionItemRow from './ActionItemRow';
import ActionItemForm from './ActionItemForm';
import Modal from '../ui/Modal';
import ConfirmDialog from '../ui/ConfirmDialog';
import Pagination from '../ui/Pagination';
import SortSelect from '../ui/SortSelect';
import EmptyState from '../ui/EmptyState';
import Button from '../ui/Button';

const PAGE_SIZE = 10;

const sortOptions = [
  { value: 'updated_at', label: 'Last updated' },
  { value: 'created_at', label: 'Date created' },
  { value: 'description', label: 'Description' },
];

export default function ActionItemsSection() {
  const [items, setItems] = useState<ActionItem[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [completedOnly, setCompletedOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<ActionItemListParams['sortBy']>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const [createOpen, setCreateOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<ActionItem | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const result = await listActionItems({
        completedOnly,
        page,
        pageSize: PAGE_SIZE,
        sortBy,
        sortOrder,
      });
      setItems(result.data);
      setTotal(result.total);
      setTotalPages(result.totalPages);
    } catch (err: any) {
      setError(err.message ?? 'Failed to load action items');
    } finally {
      setLoading(false);
    }
  }, [completedOnly, page, sortBy, sortOrder]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const handleCreate = async (description: string) => {
    await createActionItem(description);
    setCreateOpen(false);
    setPage(1);
    fetch();
  };

  const handleToggle = async (item: ActionItem) => {
    setTogglingId(item.id);
    try {
      await toggleActionItem(item.id, !item.completed);
      fetch();
    } catch (err: any) {
      setError(err.message ?? 'Failed to update item');
    } finally {
      setTogglingId(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await deleteActionItem(deleteTarget.id);
      setDeleteTarget(null);
      if (items.length === 1 && page > 1) setPage((p) => p - 1);
      else fetch();
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleCompletedOnlyChange = (checked: boolean) => {
    setCompletedOnly(checked);
    setPage(1);
  };

  const handleSortByChange = (val: string) => {
    setSortBy(val as ActionItemListParams['sortBy']);
    setPage(1);
  };

  const handleSortOrderChange = (order: 'asc' | 'desc') => {
    setSortOrder(order);
    setPage(1);
  };

  const completedCount = completedOnly ? total : items.filter((i) => i.completed).length;
  const openCount = completedOnly ? 0 : items.filter((i) => !i.completed).length;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer group select-none">
            <div className="relative">
              <input
                type="checkbox"
                checked={completedOnly}
                onChange={(e) => handleCompletedOnlyChange(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-colors" />
              <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4" />
            </div>
            <span className="text-sm font-medium text-gray-700">Show completed only</span>
          </label>

          {!loading && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              {!completedOnly && (
                <span className="bg-blue-100 text-blue-700 font-medium px-2 py-0.5 rounded-full">
                  {openCount} open
                </span>
              )}
              <span className="bg-emerald-100 text-emerald-700 font-medium px-2 py-0.5 rounded-full">
                {completedCount} done
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <SortSelect
            sortBy={sortBy ?? 'updated_at'}
            sortOrder={sortOrder}
            options={sortOptions}
            onSortByChange={handleSortByChange}
            onSortOrderChange={handleSortOrderChange}
          />
          <Button onClick={() => setCreateOpen(true)} size="md">
            <Plus size={14} />
            New Item
          </Button>
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-xl p-3.5 animate-pulse flex gap-3">
              <div className="w-4 h-4 bg-gray-200 rounded-full mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="h-3.5 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-100 rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={CheckSquare}
          title={completedOnly ? 'No completed items' : 'No action items yet'}
          description={
            completedOnly
              ? 'You have no completed action items.'
              : 'Start tracking tasks by creating your first action item.'
          }
          action={
            !completedOnly ? (
              <Button onClick={() => setCreateOpen(true)} size="sm">
                <Plus size={12} />
                Create item
              </Button>
            ) : undefined
          }
        />
      ) : (
        <>
          <div className="flex flex-col gap-2">
            {items.map((item) => (
              <ActionItemRow
                key={item.id}
                item={item}
                onToggle={handleToggle}
                onDelete={setDeleteTarget}
                toggling={togglingId === item.id}
              />
            ))}
          </div>
          <Pagination
            page={page}
            totalPages={totalPages}
            total={total}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New Action Item">
        <ActionItemForm onSubmit={handleCreate} onCancel={() => setCreateOpen(false)} />
      </Modal>

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Action Item"
        message="Are you sure you want to delete this action item? This action cannot be undone."
        loading={deleteLoading}
      />
    </div>
  );
}
