import { api } from "../lib/axios";
import type { User, Company } from "../types";

export const authApi = {
  login: async (username: string, password: string): Promise<{ access_token: string }> => {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const { data } = await api.post("/auth/token", form);
    return data;
  },
  register: async (payload: {
    email: string; username: string; full_name: string; password: string;
  }): Promise<User> => {
    const { data } = await api.post("/auth/register", payload);
    return data;
  },
  me: async (): Promise<User> => {
    const { data } = await api.get("/auth/me");
    return data;
  },
  switchCompany: async (company_id: string): Promise<User> => {
    const { data } = await api.post("/auth/switch-company", { company_id });
    return data;
  },
  myCompanies: async (): Promise<{ company: Company; role: string }[]> => {
    const { data } = await api.get("/auth/my-companies");
    return data;
  },
};
