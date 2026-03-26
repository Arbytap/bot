import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { documentsApi } from "../../../api/documents";
import { Badge } from "../../../components/ui/Badge";
import { Spinner } from "../../../components/ui/Spinner";
import { Pagination } from "../../../components/ui/Pagination";
import { EmptyState } from "../../../components/ui/EmptyState";
import {
  DOC_TYPE_LABELS, DOC_STATUS_LABELS, DOC_STATUS_COLORS, formatDate,
} from "../../../lib/helpers";
import type { DocType, DocStatus } from "../../../types";

interface Props { projectId: string }

export function DocumentsTab({ projectId }: Props) {
  const navigate = useNavigate();
  const [docType, setDocType] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["documents", projectId, docType, page],
    queryFn: () => documentsApi.list({
      project_id: projectId,
      doc_type: docType || undefined,
      page,
      page_size: 20,
    }),
  });

  const DOC_TYPES = [
    { value: "", label: "Все типы" },
    { value: "project_doc", label: "ПД" },
    { value: "working_doc", label: "РД" },
    { value: "as_built", label: "ИД" },
    { value: "contract", label: "Договоры" },
    { value: "order", label: "Приказы" },
    { value: "report", label: "Отчёты" },
  ];

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        {DOC_TYPES.map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setDocType(opt.value); setPage(1); }}
            className={`text-xs px-3 py-1 rounded-full transition-colors ${
              docType === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner /></div>
        ) : !data?.items.length ? (
          <EmptyState title="Нет документов по этому проекту" />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                  <th className="px-4 py-3">Код</th>
                  <th className="px-4 py-3">Наименование</th>
                  <th className="px-4 py-3">Тип</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Версия</th>
                  <th className="px-4 py-3">Обновлён</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((doc) => (
                  <tr
                    key={doc.id}
                    className="table-row-hover"
                    onClick={() => navigate(`/documents/${doc.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-sm text-blue-700">{doc.code || "—"}</td>
                    <td className="px-4 py-3 text-gray-900 font-medium max-w-xs truncate">{doc.name}</td>
                    <td className="px-4 py-3">
                      <Badge label={DOC_TYPE_LABELS[doc.doc_type as DocType]} className="bg-indigo-100 text-indigo-700" />
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        label={DOC_STATUS_LABELS[doc.status as DocStatus]}
                        className={DOC_STATUS_COLORS[doc.status as DocStatus]}
                      />
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{doc.version}</td>
                    <td className="px-4 py-3 text-gray-400">{formatDate(doc.updated_at)}</td>
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
