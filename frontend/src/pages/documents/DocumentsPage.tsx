import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { documentsApi } from "../../api/documents";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Pagination } from "../../components/ui/Pagination";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import {
  DOC_TYPE_LABELS, DOC_STATUS_LABELS, DOC_STATUS_COLORS, formatDate,
} from "../../lib/helpers";
import type { DocType, DocStatus } from "../../types";

const DOC_TYPES = [
  { value: "", label: "Все типы" },
  { value: "project_doc", label: "ПД" },
  { value: "working_doc", label: "РД" },
  { value: "as_built", label: "ИД" },
  { value: "contract", label: "Договоры" },
  { value: "order", label: "Приказы" },
  { value: "report", label: "Отчёты" },
  { value: "other", label: "Прочее" },
];

export function DocumentsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [docType, setDocType] = useState("");
  const [docStatus, setDocStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["documents-all", page, docType, docStatus],
    queryFn: () => documentsApi.list({
      doc_type: docType || undefined,
      status: docStatus || undefined,
      page,
      page_size: 20,
    }),
  });

  return (
    <div>
      <PageHeader
        title="Реестр документов"
        subtitle={data ? `Всего: ${data.total}` : undefined}
      />

      <div className="flex items-center gap-2 px-6 py-3 bg-white border-b border-gray-200 flex-wrap">
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
        <div className="h-4 w-px bg-gray-200 mx-1" />
        {[
          { value: "", label: "Все статусы" },
          { value: "draft", label: "Черновики" },
          { value: "on_approval", label: "На согласовании" },
          { value: "approved", label: "Утверждены" },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setDocStatus(opt.value); setPage(1); }}
            className={`text-xs px-3 py-1 rounded-full transition-colors ${
              docStatus === opt.value
                ? "bg-indigo-600 text-white"
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
          <EmptyState title="Нет документов" />
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
                  <th className="px-4 py-3 text-center">📎</th>
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
                    <td className="px-4 py-3 text-gray-400 text-xs">{doc.version}</td>
                    <td className="px-4 py-3 text-center text-gray-400 text-xs">
                      {doc.files_count > 0 ? doc.files_count : "—"}
                    </td>
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
