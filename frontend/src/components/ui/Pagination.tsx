interface PaginationProps {
  page: number;
  pages: number;
  total: number;
  onPageChange: (p: number) => void;
}

export function Pagination({ page, pages, total, onPageChange }: PaginationProps) {
  if (pages <= 1) return null;
  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-white">
      <span className="text-sm text-gray-500">Всего: {total}</span>
      <div className="flex gap-1">
        <button
          className="btn-secondary px-3 py-1 text-xs"
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          ←
        </button>
        <span className="px-3 py-1 text-xs text-gray-600">
          {page} / {pages}
        </span>
        <button
          className="btn-secondary px-3 py-1 text-xs"
          disabled={page === pages}
          onClick={() => onPageChange(page + 1)}
        >
          →
        </button>
      </div>
    </div>
  );
}
