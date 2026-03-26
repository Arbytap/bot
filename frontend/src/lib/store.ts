import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, Company } from "../types";

interface AuthState {
  token: string | null;
  user: User | null;
  currentCompany: Company | null;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  setCurrentCompany: (company: Company | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      currentCompany: null,
      setToken: (token) => {
        localStorage.setItem("access_token", token);
        set({ token });
      },
      setUser: (user) => set({ user }),
      setCurrentCompany: (company) => set({ currentCompany: company }),
      logout: () => {
        localStorage.removeItem("access_token");
        set({ token: null, user: null, currentCompany: null });
      },
    }),
    { name: "auth-store", partialize: (s) => ({ token: s.token, user: s.user, currentCompany: s.currentCompany }) }
  )
);
