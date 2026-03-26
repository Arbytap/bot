import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sedApi } from "../../api/sed";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Pagination } from "../../components/ui/Pagination";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { LETTER_STATUS_LABELS, LETTER_STATUS_COLORS, formatDate } from "../../lib/helpers";
import type { LetterStatus } from "../../types";

const STATUS_OPTS = [
  { value: "", label: "Все статусы" },
  { value: "received", label: "Получено" },
  { value: "in_work", label: "В работе" },
  { value: "done", label: "Исполнено" },
  { value: "archived", label: "Архив" },
];

export function IncomingPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["incoming", page, status],
    queryFn: () => sedApi.listIncoming({ page, page_size: 20, status: status || undefined }),
  });

  return (
    <div>
      <PageHeader
        title="Журнал входящих"
        subtitle={data ? `Всего: ${data.total}` : undefined}
        actions={
          <button className="btn-primary" onClick={() => navigate("/letters/new?type=incoming")}>
            + Зарегистрировать
          </button>
        }
      />

      <div className="flex items-center gap-3 px-6 py-3 bg-white border-b border-gray-200">
        {STATUS_OPTS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setStatus(opt.value); setPage(1); }}
            className={`text-sm px-3 py-1 rounded-full transition-colors ${
              status === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="card mx-6 my-4">
        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner /></div>
        ) : !data?.items.length ? (
          <EmptyState title="Входящих писем нет" />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                  <th className="px-4 py-3">Наш №</th>
                  <th className="px-4 py-3">№ контрагента</th>
                  <th className="px-4 py-3">Дата</th>
                  <th className="px-4 py-3">Тема</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3 text-center">📎</th>
                  <th className="px-4 py-3 text-center">↩</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((letter) => (
                  <tr
                    key={letter.id}
                    className="table-row-hover"
                    onClick={() => navigate(`/letters/${letter.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-sm text-blue-700 font-medium">
                      {letter.number || "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-sm">{letter.org_number || "—"}</td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(letter.letter_date)}</td>
                    <td className="px-4 py-3 text-gray-900 max-w-xs truncate">{letter.subject || "—"}</td>
                    <td className="px-4 py-3">
                      <Badge
                        label={LETTER_STATUS_LABELS[letter.status as LetterStatus]}
                        className={LETTER_STATUS_COLORS[letter.status as LetterStatus]}
                      />
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400 text-xs">
                      {letter.files_count > 0 ? letter.files_count : "—"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {letter.has_replies ? (
                        <span className="text-green-600 text-xs font-medium">Есть</span>
                      ) : (
                        <span className="text-gray-300 text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination page={data.page} pages={data.pages} total={data.total} onPageChange={setPage} />
          </>
        )}
      </div>
    </div>
  );
}
