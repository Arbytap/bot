import { Outlet, Navigate } from "react-router-dom";
import { useAuthStore } from "../../lib/store";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  const { token, currentCompany } = useAuthStore();

  if (!token) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
