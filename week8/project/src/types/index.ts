export interface Tag {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
}

export interface ActionItem {
  id: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export type SortOrder = 'asc' | 'desc';

export interface NoteListParams {
  search?: string;
  tagId?: string;
  page?: number;
  pageSize?: number;
  sortBy?: 'title' | 'created_at' | 'updated_at';
  sortOrder?: SortOrder;
}

export interface ActionItemListParams {
  completedOnly?: boolean;
  page?: number;
  pageSize?: number;
  sortBy?: 'description' | 'created_at' | 'updated_at';
  sortOrder?: SortOrder;
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
