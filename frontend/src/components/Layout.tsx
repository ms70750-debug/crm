import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { BarChart3, BookOpen, Bot, ClipboardList, LayoutDashboard, LogOut, MessageCircle, Search, Settings, Users, WalletCards } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
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

export function Layout({ children }: { children: ReactNode }) {
  const { logout, user } = useAuth();
  const visibleNav = nav.filter((item) => user && item.roles.includes(user.role));

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="panel sticky top-0 z-20 flex h-auto flex-col rounded-none border-l-0 border-t-0 lg:h-screen">
        <div className="flex items-center gap-3 border-b border-line p-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-lime text-black">
            <Bot size={22} />
          </div>
          <div>
            <div className="text-sm font-semibold text-lime">BBB Consig</div>
            <div className="text-lg font-bold tracking-wide">CRM</div>
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
                  `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${
                    isActive ? "bg-lime text-black" : "text-slate-300 hover:bg-white/5 hover:text-lime"
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
        <header className="sticky top-0 z-10 border-b border-line bg-ink/85 px-5 py-4 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-lime">Operacao consignado</p>
              <h1 className="text-xl font-semibold">BBB Consig CRM</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <div className="badge border-lime/30 text-lime">Evolution API em simulacao</div>
              <div className="badge border-yellow-400/40 text-yellow-200">Ambiente demo: nao insira dados reais</div>
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
