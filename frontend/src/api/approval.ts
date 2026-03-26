import { api } from "../lib/axios";
import type { ApprovalTask, Paginated } from "../types";

export const approvalApi = {
  listTasks: async (params: {
    project_id: string; assignee?: string; status?: string;
    page?: number; page_size?: number;
  }): Promise<Paginated<ApprovalTask>> => {
    const { data } = await api.get("/approval/tasks", { params });
    return data;
  },
  startApproval: async (payload: {
    project_id: string; title: string; letter_id?: string;
    document_id?: string; route_id?: string; assignee_id?: string;
    deadline?: string; comment?: string;
  }): Promise<ApprovalTask> => {
    const { data } = await api.post("/approval/start", payload);
    return data;
  },
  updateTask: async (id: string, payload: { status?: string; comment?: string }): Promise<ApprovalTask> => {
    const { data } = await api.patch(`/approval/tasks/${id}`, payload);
    return data;
  },
};
