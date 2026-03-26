// ─── Enums ───────────────────────────────────────────────────────────────────

export type CompanyType =
  | "customer" | "general_contractor" | "subcontractor"
  | "designer" | "supervisor" | "operator" | "other";

export type UserRole = "admin" | "manager" | "editor" | "viewer";
export type ProjectStatus = "planned" | "active" | "frozen" | "closed";
export type ProjectCompanyRole =
  | "customer" | "general_contractor" | "subcontractor"
  | "designer" | "supervisor" | "operator" | "other";

export type ChainDirection = "incoming" | "outgoing" | "mixed";
export type LetterType = "incoming" | "outgoing" | "internal";
export type LetterStatus = "received" | "in_work" | "done" | "sent" | "archived";
export type DocType =
  | "project_doc" | "working_doc" | "as_built"
  | "contract" | "order" | "report" | "other";
export type DocStatus = "draft" | "on_approval" | "approved" | "archived";
export type ApprovalStatus =
  | "pending" | "in_progress" | "approved" | "rejected" | "cancelled";

// ─── API Entities ─────────────────────────────────────────────────────────────

export interface Company {
  id: string;
  name: string;
  short_name: string;
  inn: string | null;
  kpp: string | null;
  company_type: CompanyType;
  is_internal: boolean;
  is_active: boolean;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  current_company_id: string | null;
}

export interface ProjectCompanyOut {
  id: string;
  project_id: string;
  company_id: string;
  role: ProjectCompanyRole;
  company: Company;
}

export interface Project {
  id: string;
  code: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  start_date: string | null;
  end_date: string | null;
  owner_company_id: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  owner_company: Company;
  project_companies: ProjectCompanyOut[];
}

export interface ProjectSummary {
  project_id: string;
  letters_count: number;
  incoming_count: number;
  outgoing_count: number;
  documents_count: number;
  approval_tasks_count: number;
  chains_count: number;
}

export interface Chain {
  id: string;
  project_id: string;
  subject: string;
  direction: ChainDirection;
  main_company_id: string | null;
  created_at: string;
  letters_count: number;
}

export interface LetterFileOut {
  id: string;
  letter_id: string;
  filename: string;
  original_name: string;
  content_type: string;
  size: number;
  uploaded_at: string;
}

export interface Letter {
  id: string;
  chain_id: string;
  project_id: string;
  owner_company_id: string;
  letter_type: LetterType;
  letter_date: string | null;
  number: string | null;
  org_number: string | null;
  from_company_id: string | null;
  to_company_id: string | null;
  subject: string | null;
  body: string | null;
  status: LetterStatus;
  reply_to_id: string | null;
  resolution: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
  files_count: number;
  has_replies: boolean;
}

export interface LetterDetail extends Letter {
  owner_company: Company;
  from_company: Company | null;
  to_company: Company | null;
  files: LetterFileOut[];
}

export interface LetterThread {
  letter: LetterDetail;
  reply_to: Letter | null;
  replies: Letter[];
  chain_letters: Letter[];
}

export interface DocumentFileOut {
  id: string;
  document_id: string;
  filename: string;
  original_name: string;
  content_type: string;
  size: number;
  version: string;
  uploaded_at: string;
}

export interface ProjectDocument {
  id: string;
  project_id: string;
  owner_company_id: string;
  doc_type: DocType;
  code: string | null;
  name: string;
  description: string | null;
  status: DocStatus;
  version: string;
  linked_letter_id: string | null;
  created_at: string;
  updated_at: string;
  files_count: number;
}

export interface DocumentDetail extends ProjectDocument {
  owner_company: Company;
  files: DocumentFileOut[];
}

export interface ApprovalTask {
  id: string;
  project_id: string;
  route_id: string | null;
  letter_id: string | null;
  document_id: string | null;
  title: string;
  status: ApprovalStatus;
  current_step: number;
  assignee_id: string | null;
  created_by_id: string | null;
  comment: string | null;
  deadline: string | null;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
