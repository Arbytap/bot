import type {
  CompanyType, ProjectStatus, LetterType, LetterStatus,
  DocType, DocStatus, ApprovalStatus, ProjectCompanyRole, ChainDirection,
} from "../types";

export const COMPANY_TYPE_LABELS: Record<CompanyType, string> = {
  customer: "Заказчик",
  general_contractor: "Генподрядчик",
  subcontractor: "Субподрядчик",
  designer: "Проектировщик",
  supervisor: "Надзор",
  operator: "Эксплуатирующая",
  other: "Прочее",
};

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  planned: "Планируется",
  active: "Активен",
  frozen: "Заморожен",
  closed: "Закрыт",
};

export const PROJECT_STATUS_COLORS: Record<ProjectStatus, string> = {
  planned: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  frozen: "bg-blue-100 text-blue-800",
  closed: "bg-gray-100 text-gray-600",
};

export const LETTER_TYPE_LABELS: Record<LetterType, string> = {
  incoming: "Входящее",
  outgoing: "Исходящее",
  internal: "Внутреннее",
};

export const LETTER_STATUS_LABELS: Record<LetterStatus, string> = {
  received: "Получено",
  in_work: "В работе",
  done: "Исполнено",
  sent: "Отправлено",
  archived: "В архиве",
};

export const LETTER_STATUS_COLORS: Record<LetterStatus, string> = {
  received: "bg-blue-100 text-blue-800",
  in_work: "bg-yellow-100 text-yellow-800",
  done: "bg-green-100 text-green-800",
  sent: "bg-indigo-100 text-indigo-800",
  archived: "bg-gray-100 text-gray-600",
};

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  project_doc: "ПД",
  working_doc: "РД",
  as_built: "ИД",
  contract: "Договор",
  order: "Приказ",
  report: "Отчёт",
  other: "Прочее",
};

export const DOC_STATUS_LABELS: Record<DocStatus, string> = {
  draft: "Черновик",
  on_approval: "На согласовании",
  approved: "Утверждён",
  archived: "В архиве",
};

export const DOC_STATUS_COLORS: Record<DocStatus, string> = {
  draft: "bg-gray-100 text-gray-700",
  on_approval: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  archived: "bg-gray-200 text-gray-500",
};

export const APPROVAL_STATUS_LABELS: Record<ApprovalStatus, string> = {
  pending: "Ожидает",
  in_progress: "В процессе",
  approved: "Согласовано",
  rejected: "Отклонено",
  cancelled: "Отменено",
};

export const APPROVAL_STATUS_COLORS: Record<ApprovalStatus, string> = {
  pending: "bg-gray-100 text-gray-700",
  in_progress: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  cancelled: "bg-gray-200 text-gray-500",
};

export const PROJECT_COMPANY_ROLE_LABELS: Record<ProjectCompanyRole, string> = {
  customer: "Заказчик",
  general_contractor: "Генподрядчик",
  subcontractor: "Субподрядчик",
  designer: "Проектировщик",
  supervisor: "Надзор",
  operator: "Эксплуатирующая",
  other: "Прочее",
};

export const CHAIN_DIRECTION_LABELS: Record<ChainDirection, string> = {
  incoming: "Входящая",
  outgoing: "Исходящая",
  mixed: "Смешанная",
};

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("ru-RU");
}

export function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleString("ru-RU");
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}
