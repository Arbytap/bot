import { api } from "../lib/axios";
import type { ProjectDocument, DocumentDetail, DocumentFileOut, Paginated } from "../types";

export const documentsApi = {
  list: async (params?: {
    project_id?: string; doc_type?: string; status?: string;
    page?: number; page_size?: number;
  }): Promise<Paginated<ProjectDocument>> => {
    const { data } = await api.get("/documents", { params });
    return data;
  },
  get: async (id: string): Promise<DocumentDetail> => {
    const { data } = await api.get(`/documents/${id}`);
    return data;
  },
  create: async (payload: {
    project_id: string; doc_type?: string; code?: string;
    name: string; description?: string; version?: string;
  }): Promise<ProjectDocument> => {
    const { data } = await api.post("/documents", payload);
    return data;
  },
  update: async (id: string, payload: Partial<ProjectDocument>): Promise<ProjectDocument> => {
    const { data } = await api.patch(`/documents/${id}`, payload);
    return data;
  },
  uploadFile: async (docId: string, file: File): Promise<DocumentFileOut> => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post(`/documents/${docId}/files`, form);
    return data;
  },
  downloadFileUrl: (docId: string, fileId: string) =>
    `/api/documents/${docId}/files/${fileId}`,
  linkLetter: async (docId: string, letterId: string): Promise<ProjectDocument> => {
    const { data } = await api.post(`/documents/${docId}/link-letter`, null, {
      params: { letter_id: letterId },
    });
    return data;
  },
};
