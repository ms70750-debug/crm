import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { BarChart3, BookOpen, ClipboardList, LayoutDashboard, LogOut, MessageCircle, Search, Settings, ShieldCheck, Users, WalletCards } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import type { Perfil } from "../types";
import { BrandLogo } from "./BrandLogo";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "supervisor", "operador", "parceiro"] },
  { to: "/leads", label: "Leads", icon: Users, roles: ["admin", "supervisor", "operador", "parceiro"] },
  { to: "/clientes", label: "Clientes", icon: WalletCards, roles: ["admin", "supervisor", "operador"] },
  { to: "/consulta-inss", label: "Consulta INSS", icon: Search, roles: ["admin", "supervisor", "operador"] },
  { to: "/consulta-fgts", label: "Consulta FGTS", icon: Search, roles: ["admin", "supervisor", "operador"] },
  { to: "/propostas", label: "Propostas", icon: BarChart3, roles: ["admin", "supervisor", "operador", "parceiro"] },
  { to: "/tarefas", label: "Tarefas", icon: ClipboardList, roles: ["admin", "supervisor", "operador"] },
  { to: "/whatsapp", label: "WhatsApp", icon: MessageCircle, roles: ["admin", "supervisor", "operador"] },
  { to: "/treinamentos", label: "Treinamentos", icon: BookOpen, roles: ["admin", "supervisor", "operador", "parceiro"] },
  { to: "/admin", label: "Administracao", icon: Settings, roles: ["admin", "supervisor"] },
];

const demoModeEnabled = import.meta.env.VITE_DEMO_MODE === "true";

export function Layout({ children }: { children: ReactNode }) {
  const { logout, user } = useAuth();
  const visibleNav = nav.filter((item) => user && item.roles.includes(user.role));

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="panel sticky top-0 z-20 flex h-auto flex-col rounded-none border-l-0 border-t-0 lg:h-screen">
        <div className="border-b border-line p-5">
          <BrandLogo />
          <div className="mt-4 flex items-center gap-2 rounded-md bg-[#eef5ff] px-3 py-2 text-xs font-medium text-lime">
            <ShieldCheck size={15} /> Operacao interna segura
          </div>
        </div>
        <nav className="grid gap-1 p-3">
          {visibleNav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition ${
                    isActive ? "bg-lime text-white shadow-[0_10px_24px_rgba(11,94,215,0.18)]" : "text-slate-600 hover:bg-[#eef5ff] hover:text-lime"
                  }`
                }
              >
                <Icon size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-line bg-white/90 px-5 py-4 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-lime">Operacao consignado</p>
              <h1 className="text-xl font-semibold text-ink">BBB Consig CRM</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {demoModeEnabled && <div className="badge border-lime/30 text-lime">Evolution API em simulacao</div>}
              {demoModeEnabled && <div className="badge border-amber-200 bg-amber-50 text-amber-700">Ambiente demo: nao insira dados reais</div>}
              {user && <div className="badge">{user.nome} - {roleLabel(user.role)}</div>}
              <button
                className="btn-secondary py-1 text-xs"
                onClick={async () => {
                  await logout();
                  window.location.assign("/login");
                }}
              >
                <LogOut size={14} /> Sair
              </button>
            </div>
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-5">{children}</div>
      </main>
    </div>
  );
}

function roleLabel(role: Perfil) {
  return {
    admin: "Administrador",
    supervisor: "Supervisor",
    operador: "Operador",
    parceiro: "Parceiro",
  }[role];
}
