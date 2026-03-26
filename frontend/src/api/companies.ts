import { api } from "../lib/axios";
import type { Company, Paginated } from "../types";

export const companiesApi = {
  list: async (params?: { page?: number; page_size?: number }): Promise<Paginated<Company>> => {
    const { data } = await api.get("/companies", { params });
    return data;
  },
  get: async (id: string): Promise<Company> => {
    const { data } = await api.get(`/companies/${id}`);
    return data;
  },
  create: async (payload: Partial<Company>): Promise<Company> => {
    const { data } = await api.post("/companies", payload);
    return data;
  },
};
