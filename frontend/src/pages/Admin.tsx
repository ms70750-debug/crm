import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import type { User } from "../types";

export function Admin() {
  const users = useAsync<User[]>(() => api.get("/auth/users"));
  const whatsapp = useAsync<{ mode: string; health: string; real_send_enabled: boolean; message: string }>(() => api.get("/whatsapp/status"));

  return (
    <>
      <PageHeader title="Administracao" subtitle="Usuarios ficticios, perfis e configuracoes gerais em modo seguro." />
      <div className="grid gap-5 lg:grid-cols-2">
        <Panel>
          <h3 className="mb-4 font-semibold">Usuarios ficticios</h3>
          <div className="grid gap-3">
            {(users.data ?? []).map((user) => (
              <div className="rounded-md border border-line bg-white/5 p-3" key={user.id}>
                <strong>{user.nome}</strong>
                <div className="text-sm text-slate-400">{user.email}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="badge">{roleLabel(user.role)}</span>
                  <span className="badge text-lime">{user.ativo ? "Ativo" : "Inativo"}</span>
                </div>
              </div>
            ))}
            {!users.data && <div className="text-sm text-slate-400">Carregando usuarios...</div>}
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Evolution API</h3>
          <div className="grid gap-3">
            <label className="text-sm text-slate-400">Modo<input className="input mt-1" value="simulation" readOnly /></label>
            <label className="text-sm text-slate-400">URL<input className="input mt-1" value="Nao configurada nesta versao" readOnly /></label>
            <label className="text-sm text-slate-400">Envio real<input className="input mt-1 text-lime" value="Bloqueado" readOnly /></label>
            <label className="text-sm text-slate-400">Health<input className="input mt-1" value={whatsapp.data?.health ?? "simulated"} readOnly /></label>
            <p className="text-sm text-slate-300">{whatsapp.data?.message ?? "Nenhuma mensagem real e enviada nesta fase."}</p>
          </div>
        </Panel>
        <Panel className="lg:col-span-2">
          <h3 className="mb-4 font-semibold">Configuracoes gerais</h3>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-md border border-line bg-white/5 p-3"><span className="text-sm text-slate-400">Pipeline</span><strong className="block">Consignado padrao</strong></div>
            <div className="rounded-md border border-line bg-white/5 p-3"><span className="text-sm text-slate-400">Ambiente</span><strong className="block">Local</strong></div>
            <div className="rounded-md border border-line bg-white/5 p-3"><span className="text-sm text-slate-400">Dados</span><strong className="block">Ficticios</strong></div>
          </div>
        </Panel>
      </div>
    </>
  );
}

function roleLabel(role: User["role"]) {
  return {
    admin: "Administrador",
    supervisor: "Supervisor",
    operador: "Operador/Vendedor",
    parceiro: "Parceiro",
  }[role];
}
