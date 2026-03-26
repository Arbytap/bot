import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectsApi } from "../../api/projects";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Pagination } from "../../components/ui/Pagination";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import {
  PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS, formatDate,
} from "../../lib/helpers";
import type { ProjectStatus } from "../../types";

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "Все статусы" },
  { value: "planned", label: "Планируются" },
  { value: "active", label: "Активные" },
  { value: "frozen", label: "Заморожены" },
  { value: "closed", label: "Закрытые" },
];

export function ProjectsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["projects", page, status],
    queryFn: () => projectsApi.list({ page, page_size: 20, status: status || undefined }),
  });

  return (
    <div>
      <PageHeader
        title="Проекты"
        subtitle={data ? `Всего: ${data.total}` : undefined}
        actions={
          <button className="btn-primary" onClick={() => navigate("/projects/new")}>
            + Новый проект
          </button>
        }
      />

      {/* Filters */}
      <div className="flex items-center gap-3 px-6 py-3 bg-white border-b border-gray-200">
        {STATUS_OPTIONS.map((opt) => (
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
          <EmptyState
            title="Нет проектов"
            description="Создайте первый проект или убедитесь, что вашей организации открыт доступ."
          />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100">
                  <th className="px-4 py-3">Код</th>
                  <th className="px-4 py-3">Наименование</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Начало</th>
                  <th className="px-4 py-3">Окончание</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((project) => (
                  <tr
                    key={project.id}
                    className="table-row-hover"
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <td className="px-4 py-3 font-mono text-sm text-blue-700 font-medium">
                      {project.code}
                    </td>
                    <td className="px-4 py-3 text-gray-900 font-medium">{project.name}</td>
                    <td className="px-4 py-3">
                      <Badge
                        label={PROJECT_STATUS_LABELS[project.status as ProjectStatus]}
                        className={PROJECT_STATUS_COLORS[project.status as ProjectStatus]}
                      />
                    </td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(project.start_date)}</td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(project.end_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination
              page={data.page}
              pages={data.pages}
              total={data.total}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}
