import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

export function Admin() {
  return (
    <>
      <PageHeader title="Administracao" subtitle="Usuarios ficticios, perfis e configuracoes gerais em modo seguro." />
      <div className="grid gap-5 lg:grid-cols-2">
        <Panel>
          <h3 className="mb-4 font-semibold">Usuarios ficticios</h3>
          {["Ana - Gestora", "Bruno - Consultor", "Marina - Operacao"].map((user) => <div className="mb-3 rounded-md border border-line bg-white/5 p-3" key={user}>{user}</div>)}
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Evolution API</h3>
          <div className="grid gap-3">
            <label className="text-sm text-slate-400">Modo<input className="input mt-1" value="simulation" readOnly /></label>
            <label className="text-sm text-slate-400">URL<input className="input mt-1" value="Nao configurada nesta versao" readOnly /></label>
            <label className="text-sm text-slate-400">Envio real<input className="input mt-1 text-lime" value="Bloqueado" readOnly /></label>
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
