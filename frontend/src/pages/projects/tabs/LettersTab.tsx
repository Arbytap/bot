import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sedApi } from "../../../api/sed";
import { Badge } from "../../../components/ui/Badge";
import { Spinner } from "../../../components/ui/Spinner";
import { Pagination } from "../../../components/ui/Pagination";
import { EmptyState } from "../../../components/ui/EmptyState";
import {
  LETTER_TYPE_LABELS, LETTER_STATUS_LABELS, LETTER_STATUS_COLORS, formatDate,
} from "../../../lib/helpers";
import type { LetterType, LetterStatus } from "../../../types";

interface Props { projectId: string }

export function LettersTab({ projectId }: Props) {
  const navigate = useNavigate();
  const [letterType, setLetterType] = useState<string>("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["letters", projectId, letterType, page],
    queryFn: () =>
      letterType === "outgoing"
        ? sedApi.listOutgoing({ project_id: projectId, page, page_size: 20 })
        : sedApi.listIncoming({ project_id: projectId, page, page_size: 20 }),
  });

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        {[
          { value: "", label: "Входящие" },
          { value: "outgoing", label: "Исходящие" },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setLetterType(opt.value); setPage(1); }}
            className={`btn ${letterType === opt.value ? "btn-primary" : "btn-secondary"}`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner /></div>
        ) : !data?.items.length ? (
          <EmptyState title="Нет писем по этому проекту" />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                  <th className="px-4 py-3">Номер</th>
                  <th className="px-4 py-3">Дата</th>
                  <th className="px-4 py-3">Тема</th>
                  <th className="px-4 py-3">Тип</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3 text-center">Файлы</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((letter) => (
                  <tr
                    key={letter.id}
                    className="table-row-hover"
                    onClick={() => navigate(`/letters/${letter.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-sm text-blue-700">
                      {letter.number || letter.org_number || "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(letter.letter_date)}</td>
                    <td className="px-4 py-3 text-gray-900 max-w-xs truncate">{letter.subject || "—"}</td>
                    <td className="px-4 py-3">
                      <Badge label={LETTER_TYPE_LABELS[letter.letter_type as LetterType]} className="bg-gray-100 text-gray-700" />
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        label={LETTER_STATUS_LABELS[letter.status as LetterStatus]}
                        className={LETTER_STATUS_COLORS[letter.status as LetterStatus]}
                      />
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400">
                      {letter.files_count > 0 ? `📎 ${letter.files_count}` : "—"}
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
