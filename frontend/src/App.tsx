import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/auth/LoginPage";
import { SwitchCompanyPage } from "./pages/auth/SwitchCompanyPage";
import { ProjectsPage } from "./pages/projects/ProjectsPage";
import { ProjectDetailPage } from "./pages/projects/ProjectDetailPage";
import { IncomingPage } from "./pages/sed/IncomingPage";
import { OutgoingPage } from "./pages/sed/OutgoingPage";
import { LetterDetailPage } from "./pages/sed/LetterDetailPage";
import { ChainsPage } from "./pages/sed/ChainsPage";
import { DocumentsPage } from "./pages/documents/DocumentsPage";
import { ApprovalPage } from "./pages/approval/ApprovalPage";
import { useAuthStore } from "./lib/store";

function LogoutPage() {
  const { logout } = useAuthStore();
  logout();
  return <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/logout" element={<LogoutPage />} />

        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/projects" replace />} />
          <Route path="/companies/switch" element={<SwitchCompanyPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/letters/incoming" element={<IncomingPage />} />
          <Route path="/letters/outgoing" element={<OutgoingPage />} />
          <Route path="/letters/:id" element={<LetterDetailPage />} />
          <Route path="/chains" element={<ChainsPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/approval" element={<ApprovalPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/projects" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
