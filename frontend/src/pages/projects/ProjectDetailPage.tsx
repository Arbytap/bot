import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { projectsApi } from "../../api/projects";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import {
  PROJECT_STATUS_LABELS, PROJECT_STATUS_COLORS,
  PROJECT_COMPANY_ROLE_LABELS, formatDate,
} from "../../lib/helpers";
import type { ProjectStatus, ProjectCompanyRole } from "../../types";
import { LettersTab } from "./tabs/LettersTab";
import { DocumentsTab } from "./tabs/DocumentsTab";
import { ApprovalTab } from "./tabs/ApprovalTab";

const TABS = [
  { id: "info", label: "Общие сведения" },
  { id: "companies", label: "Участники" },
  { id: "letters", label: "Переписка" },
  { id: "documents", label: "Документы" },
  { id: "approval", label: "Согласование" },
];

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tab, setTab] = useState("info");

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
  });

  const { data: summary } = useQuery({
    queryKey: ["project-summary", id],
    queryFn: () => projectsApi.summary(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="flex justify-center py-24"><Spinner size="lg" /></div>;
  }
  if (!project) return <div className="p-8 text-gray-500">Проект не найден</div>;

  return (
    <div>
      <PageHeader
        title={project.name}
        subtitle={`Код: ${project.code}`}
        actions={
          <Badge
            label={PROJECT_STATUS_LABELS[project.status as ProjectStatus]}
            className={PROJECT_STATUS_COLORS[project.status as ProjectStatus]}
          />
        }
      />

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-6 gap-3 px-6 py-4 bg-gray-50 border-b border-gray-200">
          {[
            { label: "Писем", value: summary.letters_count },
            { label: "Входящих", value: summary.incoming_count },
            { label: "Исходящих", value: summary.outgoing_count },
            { label: "Документов", value: summary.documents_count },
            { label: "Цепочек", value: summary.chains_count },
            { label: "Задач", value: summary.approval_tasks_count },
          ].map((s) => (
            <div key={s.label} className="card p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{s.value}</div>
              <div className="text-xs text-gray-500 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex gap-0">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {tab === "info" && (
          <div className="max-w-2xl space-y-4">
            <div className="card p-5 grid grid-cols-2 gap-4">
              <Field label="Код проекта" value={project.code} />
              <Field label="Статус" value={PROJECT_STATUS_LABELS[project.status as ProjectStatus]} />
              <Field label="Дата начала" value={formatDate(project.start_date)} />
              <Field label="Дата окончания" value={formatDate(project.end_date)} />
              <div className="col-span-2">
                <Field label="Владелец" value={project.owner_company.short_name} />
              </div>
              {project.description && (
                <div className="col-span-2">
                  <Field label="Описание" value={project.description} />
                </div>
              )}
            </div>
          </div>
        )}

        {tab === "companies" && (
          <div className="max-w-2xl">
            <div className="card overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                    <th className="px-4 py-3">Организация</th>
                    <th className="px-4 py-3">Роль</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {project.project_companies.map((pc) => (
                    <tr key={pc.id}>
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900">{pc.company.short_name}</div>
                        <div className="text-xs text-gray-400">{pc.company.inn && `ИНН: ${pc.company.inn}`}</div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          label={PROJECT_COMPANY_ROLE_LABELS[pc.role as ProjectCompanyRole]}
                          className="bg-indigo-100 text-indigo-700"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === "letters" && <LettersTab projectId={project.id} />}
        {tab === "documents" && <DocumentsTab projectId={project.id} />}
        {tab === "approval" && <ApprovalTab projectId={project.id} />}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-gray-400 uppercase tracking-wide">{label}</div>
      <div className="text-sm text-gray-900 font-medium mt-0.5">{value}</div>
    </div>
  );
}
