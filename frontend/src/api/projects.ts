import { api } from "../lib/axios";
import type { Project, ProjectDetail, ProjectSummary, ProjectCompanyOut, Paginated } from "../types";

export const projectsApi = {
  list: async (params?: { status?: string; page?: number; page_size?: number }): Promise<Paginated<Project>> => {
    const { data } = await api.get("/projects", { params });
    return data;
  },
  get: async (id: string): Promise<ProjectDetail> => {
    const { data } = await api.get(`/projects/${id}`);
    return data;
  },
  create: async (payload: {
    code: string; name: string; description?: string;
    status?: string; start_date?: string; end_date?: string; owner_company_id: string;
  }): Promise<ProjectDetail> => {
    const { data } = await api.post("/projects", payload);
    return data;
  },
  update: async (id: string, payload: Partial<Project>): Promise<ProjectDetail> => {
    const { data } = await api.patch(`/projects/${id}`, payload);
    return data;
  },
  summary: async (id: string): Promise<ProjectSummary> => {
    const { data } = await api.get(`/projects/${id}/summary`);
    return data;
  },
  addCompany: async (projectId: string, payload: { company_id: string; role: string }): Promise<ProjectCompanyOut> => {
    const { data } = await api.post(`/projects/${projectId}/companies`, payload);
    return data;
  },
  removeCompany: async (projectId: string, companyId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}/companies/${companyId}`);
  },
};
