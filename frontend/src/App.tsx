import { Routes, Route, Navigate } from "react-router-dom";
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
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/leads" element={<Leads />} />
        <Route path="/leads/:id" element={<LeadDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/clientes" element={<Clients />} />
        <Route path="/consulta-inss" element={<INSS />} />
        <Route path="/consulta-fgts" element={<FGTS />} />
        <Route path="/propostas" element={<Proposals />} />
        <Route path="/tarefas" element={<Tasks />} />
        <Route path="/whatsapp" element={<WhatsApp />} />
        <Route path="/treinamentos" element={<Trainings />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Layout>
  );
}
