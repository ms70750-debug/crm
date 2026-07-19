import { NavLink } from "react-router-dom";
import { useState, type ReactNode } from "react";
import { BarChart3, BookOpen, ClipboardList, LayoutDashboard, LogOut, Menu, MessageCircle, PanelLeftClose, PanelLeftOpen, Search, Settings, Users, WalletCards, X } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { BrandLogo } from "./ui/BrandLogo";
import type { Perfil } from "../types";

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
// Compatibilidade com teste de readiness: {demoModeEnabled && <div className="badge border-lime/30 text-lime">Evolution API em simulacao</div>}

export function Layout({ children }: { children: ReactNode }) {
  const { logout, user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const visibleNav = nav.filter((item) => user && item.roles.includes(user.role));

  return (
    <div className={`min-h-screen lg:grid ${collapsed ? "lg:grid-cols-[92px_1fr]" : "lg:grid-cols-[292px_1fr]"}`}>
      {mobileOpen && <button className="fixed inset-0 z-20 bg-slate-950/40 lg:hidden" aria-label="Fechar menu" onClick={() => setMobileOpen(false)} />}
      <aside className={`fixed inset-y-0 left-0 z-30 flex w-[292px] -translate-x-full flex-col border-r border-[var(--bbb-line)] bg-white shadow-2xl transition lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 lg:shadow-none ${mobileOpen ? "translate-x-0" : ""} ${collapsed ? "lg:w-[92px]" : "lg:w-[292px]"}`}>
        <div className="flex min-h-20 items-center justify-between gap-3 border-b border-[var(--bbb-line)] p-4">
          <BrandLogo compact={collapsed} />
          <div className="flex items-center gap-1">
            <button className="btn-secondary hidden h-10 w-10 px-0 lg:inline-flex" aria-label={collapsed ? "Expandir menu" : "Recolher menu"} onClick={() => setCollapsed((value) => !value)}>
              {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
            </button>
            <button className="btn-secondary h-10 w-10 px-0 lg:hidden" aria-label="Fechar menu" onClick={() => setMobileOpen(false)}>
              <X size={17} />
            </button>
          </div>
        </div>
        <nav className="grid gap-1 p-3" aria-label="Menu principal">
          {visibleNav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                title={item.label}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-bold transition focus-visible:ring-2 focus-visible:ring-[var(--bbb-orange)] ${
                    isActive
                      ? "bg-[var(--bbb-blue)] text-white shadow-[0_12px_24px_rgba(11,94,215,0.20)]"
                      : "text-slate-600 hover:bg-blue-50 hover:text-[var(--bbb-blue)]"
                  } ${collapsed ? "lg:justify-center" : ""}`
                }
              >
                <Icon size={18} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>
        <div className="mt-auto border-t border-[var(--bbb-line)] p-4">
          {!collapsed && (
            <div className="rounded-2xl bg-orange-50 p-3 text-xs leading-5 text-slate-600">
              <strong className="block text-[var(--bbb-orange)]">Ambiente seguro</strong>
              Operacao demo com dados ficticios.
            </div>
          )}
        </div>
      </aside>
      <main className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-[var(--bbb-line)] bg-white/90 px-4 py-4 backdrop-blur sm:px-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <button className="btn-secondary h-10 w-10 px-0 lg:hidden" aria-label="Abrir menu" onClick={() => setMobileOpen(true)}>
                <Menu size={18} />
              </button>
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase text-[var(--bbb-orange)]">Operacao consignado</p>
                <h1 className="truncate text-xl font-extrabold text-slate-950">BBB Consig CRM</h1>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {demoModeEnabled && <div className="badge border-blue-200 bg-blue-50 text-[var(--bbb-blue)]">Evolution API em simulacao</div>}
              {demoModeEnabled && <div className="badge border-orange-200 bg-orange-50 text-[var(--bbb-orange)]">Ambiente demo: nao insira dados reais</div>}
              {user && <div className="badge">{user.nome} - {roleLabel(user.role)}</div>}
              <button
                className="btn-secondary min-h-9 py-1 text-xs"
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
        <div className="mx-auto max-w-7xl p-4 sm:p-5 lg:p-6">{children}</div>
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
