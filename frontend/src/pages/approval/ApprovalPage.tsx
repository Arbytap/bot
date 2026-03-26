import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams, useNavigate } from "react-router-dom";
import { approvalApi } from "../../api/approval";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Pagination } from "../../components/ui/Pagination";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { APPROVAL_STATUS_LABELS, APPROVAL_STATUS_COLORS, formatDate } from "../../lib/helpers";
import type { ApprovalStatus } from "../../types";

export function ApprovalPage() {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("project_id") || "";
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["approval-tasks-global", projectId, status, page],
    queryFn: () => approvalApi.listTasks({ project_id: projectId, status: status || undefined, page, page_size: 20 }),
    enabled: !!projectId,
  });

  if (!projectId) {
    return (
      <div>
        <PageHeader title="Согласование" />
        <EmptyState
          title="Выберите проект"
          description="Для просмотра задач согласования укажите проект в параметрах URL."
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Согласование" subtitle={data ? `Задач: ${data.total}` : undefined} />
      <div className="flex gap-2 px-6 py-3 bg-white border-b border-gray-200">
        {[
          { value: "", label: "Все" },
          { value: "pending", label: "Ожидают" },
          { value: "in_progress", label: "В процессе" },
          { value: "approved", label: "Согласованы" },
          { value: "rejected", label: "Отклонены" },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setStatus(opt.value); setPage(1); }}
            className={`text-xs px-3 py-1 rounded-full transition-colors ${
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
          <EmptyState title="Нет задач согласования" />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                  <th className="px-4 py-3">Задача</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Привязка</th>
                  <th className="px-4 py-3">Срок</th>
                  <th className="px-4 py-3">Создана</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">{task.title}</td>
                    <td className="px-4 py-3">
                      <Badge
                        label={APPROVAL_STATUS_LABELS[task.status as ApprovalStatus]}
                        className={APPROVAL_STATUS_COLORS[task.status as ApprovalStatus]}
                      />
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">
                      {task.letter_id ? "📥 Письмо" : task.document_id ? "📄 Документ" : "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(task.deadline)}</td>
                    <td className="px-4 py-3 text-gray-400">{formatDate(task.created_at)}</td>
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
