import { api } from "../lib/axios";
import type { Chain, Letter, LetterDetail, LetterThread, LetterFileOut, Paginated } from "../types";

export const sedApi = {
  // Chains
  listChains: async (params?: {
    project_id?: string; company_id?: string; direction?: string;
    page?: number; page_size?: number;
  }): Promise<Paginated<Chain>> => {
    const { data } = await api.get("/sed/chains", { params });
    return data;
  },
  createChain: async (payload: {
    project_id: string; subject: string; direction?: string; main_company_id?: string;
  }): Promise<Chain> => {
    const { data } = await api.post("/sed/chains", payload);
    return data;
  },
  updateChain: async (id: string, payload: Partial<Chain>): Promise<Chain> => {
    const { data } = await api.patch(`/sed/chains/${id}`, payload);
    return data;
  },

  // Letters
  listIncoming: async (params?: {
    project_id?: string; chain_id?: string; status?: string;
    from_company_id?: string; page?: number; page_size?: number;
  }): Promise<Paginated<Letter>> => {
    const { data } = await api.get("/sed/letters/incoming", { params });
    return data;
  },
  listOutgoing: async (params?: {
    project_id?: string; chain_id?: string; status?: string;
    to_company_id?: string; page?: number; page_size?: number;
  }): Promise<Paginated<Letter>> => {
    const { data } = await api.get("/sed/letters/outgoing", { params });
    return data;
  },
  getLetter: async (id: string): Promise<LetterDetail> => {
    const { data } = await api.get(`/sed/letters/${id}`);
    return data;
  },
  createLetter: async (payload: {
    chain_id: string; project_id: string; letter_type: string;
    letter_date?: string; number?: string; org_number?: string;
    from_company_id?: string; to_company_id?: string;
    subject?: string; body?: string; status?: string;
    reply_to_id?: string; resolution?: string; note?: string;
  }): Promise<Letter> => {
    const { data } = await api.post("/sed/letters", payload);
    return data;
  },
  updateLetter: async (id: string, payload: Partial<Letter>): Promise<Letter> => {
    const { data } = await api.patch(`/sed/letters/${id}`, payload);
    return data;
  },
  getThread: async (id: string): Promise<LetterThread> => {
    const { data } = await api.get(`/sed/letters/${id}/thread`);
    return data;
  },
  uploadFile: async (letterId: string, file: File): Promise<LetterFileOut> => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post(`/sed/letters/${letterId}/files`, form);
    return data;
  },
  downloadFileUrl: (letterId: string, fileId: string) =>
    `/api/sed/letters/${letterId}/files/${fileId}`,
};
