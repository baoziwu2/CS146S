"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Trash2, CircleCheck as CheckCircle2, Circle } from 'lucide-react';
import { ActionItem } from '@/lib/supabase';

interface ActionItemListProps {
  refresh: number;
}

export function ActionItemList({ refresh }: ActionItemListProps) {
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [completedOnly, setCompletedOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchActionItems = async () => {
    setLoading(true);
    try {
      const url = completedOnly
        ? '/api/action-items?completedOnly=true'
        : '/api/action-items';
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setActionItems(data);
      }
    } catch (error) {
      console.error('Failed to fetch action items:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActionItems();
  }, [refresh, completedOnly]);

  const handleToggleComplete = async (id: string, currentStatus: boolean) => {
    const newStatus = !currentStatus;

    setActionItems(prevItems =>
      prevItems.map(item =>
        item.id === id ? { ...item, completed: newStatus } : item
      )
    );

    try {
      const response = await fetch(`/api/action-items/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: newStatus }),
      });

      if (!response.ok) {
        setActionItems(prevItems =>
          prevItems.map(item =>
            item.id === id ? { ...item, completed: currentStatus } : item
          )
        );
      }
    } catch (error) {
      console.error('Failed to update action item:', error);
      setActionItems(prevItems =>
        prevItems.map(item =>
          item.id === id ? { ...item, completed: currentStatus } : item
        )
      );
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this action item?')) return;

    setActionItems(prevItems => prevItems.filter(item => item.id !== id));

    try {
      const response = await fetch(`/api/action-items/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        fetchActionItems();
      }
    } catch (error) {
      console.error('Failed to delete action item:', error);
      fetchActionItems();
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

  const completedCount = actionItems.filter(item => item.completed).length;
  const totalCount = actionItems.length;

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-2xl font-bold text-slate-800">Action Items</CardTitle>
              <p className="text-sm text-slate-600 mt-1">
                {completedCount} of {totalCount} completed
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="completed-only"
                checked={completedOnly}
                onCheckedChange={setCompletedOnly}
                className="data-[state=checked]:bg-emerald-600"
              />
              <Label htmlFor="completed-only" className="text-sm font-medium text-slate-700">
                Show completed only
              </Label>
            </div>
          </div>
        </CardHeader>
      </Card>

      {loading ? (
        <div className="text-center text-slate-600">Loading action items...</div>
      ) : actionItems.length === 0 ? (
        <Card className="bg-white border-emerald-200">
          <CardContent className="pt-6 text-center text-slate-500">
            {completedOnly
              ? 'No completed action items yet.'
              : 'No action items found. Add one above or create a note with action items!'}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {actionItems.map((item) => (
            <Card
              key={item.id}
              className={`bg-white border-emerald-200 hover:shadow-md transition-all ${
                item.completed ? 'opacity-75' : ''
              }`}
            >
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <button
                    onClick={() => handleToggleComplete(item.id, item.completed)}
                    className="mt-1 flex-shrink-0"
                  >
                    {item.completed ? (
                      <CheckCircle2 className="h-6 w-6 text-emerald-600" />
                    ) : (
                      <Circle className="h-6 w-6 text-slate-400 hover:text-emerald-500 transition-colors" />
                    )}
                  </button>
                  <div className="flex-1">
                    <p
                      className={`text-slate-800 ${
                        item.completed ? 'line-through text-slate-500' : ''
                      }`}
                    >
                      {item.description}
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      Created: {formatDate(item.created_at)}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleDelete(item.id)}
                    className="flex-shrink-0 hover:bg-red-50 hover:text-red-600 hover:border-red-300"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
