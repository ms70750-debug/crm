import { Routes, Route, Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { Layout } from "./components/Layout";
import { Admin } from "./pages/Admin";
import { Clients } from "./pages/Clients";
import { Dashboard } from "./pages/Dashboard";
import { FGTS } from "./pages/FGTS";
import { INSS } from "./pages/INSS";
import { LeadDetail } from "./pages/LeadDetail";
import { Leads } from "./pages/Leads";
import { Login } from "./pages/Login";
import { Proposals } from "./pages/Proposals";
import { Tasks } from "./pages/Tasks";
import { Trainings } from "./pages/Trainings";
import { WhatsApp } from "./pages/WhatsApp";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedPage><Dashboard /></ProtectedPage>} />
        <Route path="/leads" element={<ProtectedPage><Leads /></ProtectedPage>} />
        <Route path="/leads/:id" element={<ProtectedPage><LeadDetail /></ProtectedPage>} />
        <Route path="/clientes" element={<ProtectedPage roles={["admin", "supervisor", "operador"]}><Clients /></ProtectedPage>} />
        <Route path="/consulta-inss" element={<ProtectedPage roles={["admin", "supervisor", "operador"]}><INSS /></ProtectedPage>} />
        <Route path="/consulta-fgts" element={<ProtectedPage roles={["admin", "supervisor", "operador"]}><FGTS /></ProtectedPage>} />
        <Route path="/propostas" element={<ProtectedPage><Proposals /></ProtectedPage>} />
        <Route path="/tarefas" element={<ProtectedPage roles={["admin", "supervisor", "operador"]}><Tasks /></ProtectedPage>} />
        <Route path="/whatsapp" element={<ProtectedPage roles={["admin", "supervisor", "operador"]}><WhatsApp /></ProtectedPage>} />
        <Route path="/treinamentos" element={<ProtectedPage><Trainings /></ProtectedPage>} />
        <Route path="/admin" element={<ProtectedPage roles={["admin", "supervisor"]}><Admin /></ProtectedPage>} />
      </Routes>
    </AuthProvider>
  );
}

function ProtectedPage({ children, roles }: { children: ReactNode; roles?: Array<"admin" | "supervisor" | "operador" | "parceiro"> }) {
  return (
    <ProtectedRoute roles={roles}>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}
