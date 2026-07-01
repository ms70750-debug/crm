import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { BarChart3, BookOpen, Bot, ClipboardList, LayoutDashboard, LockKeyhole, MessageCircle, Search, Settings, Users, WalletCards } from "lucide-react";
import { clearAuthToken, getAuthToken } from "../lib/api";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/leads", label: "Leads", icon: Users },
  { to: "/clientes", label: "Clientes", icon: WalletCards },
  { to: "/consulta-inss", label: "Consulta INSS", icon: Search },
  { to: "/consulta-fgts", label: "Consulta FGTS", icon: Search },
  { to: "/propostas", label: "Propostas", icon: BarChart3 },
  { to: "/tarefas", label: "Tarefas", icon: ClipboardList },
  { to: "/whatsapp", label: "WhatsApp", icon: MessageCircle },
  { to: "/treinamentos", label: "Treinamentos", icon: BookOpen },
  { to: "/admin", label: "Administracao", icon: Settings },
  { to: "/login", label: "Login local", icon: LockKeyhole },
];

export function Layout({ children }: { children: ReactNode }) {
  const hasToken = Boolean(getAuthToken());

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
          {nav.map((item) => {
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
              <button
                className="btn-secondary py-1 text-xs"
                onClick={() => {
                  clearAuthToken();
                  window.location.assign("/login");
                }}
              >
                {hasToken ? "Sair" : "Sem sessao"}
              </button>
            </div>
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-5">{children}</div>
      </main>
    </div>
  );
}
