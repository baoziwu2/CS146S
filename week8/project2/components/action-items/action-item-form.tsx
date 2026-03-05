"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ActionItemFormProps {
  onSuccess: () => void;
}

export function ActionItemForm({ onSuccess }: ActionItemFormProps) {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/action-items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });

      if (response.ok) {
        setDescription('');
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to create action item:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-slate-800">Add Action Item</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              placeholder="Enter action item description..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="bg-white border-emerald-300 focus:border-emerald-500 focus:ring-emerald-500"
            />
          </div>
          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold"
          >
            {loading ? 'Adding...' : 'Add Action Item'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
