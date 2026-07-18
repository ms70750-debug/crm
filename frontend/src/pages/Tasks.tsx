import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { CrudShell, Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import { useAsync } from "../hooks/useAsync";
import { api } from "../lib/api";
import { Task } from "../types";

const schema = z.object({ titulo: z.string().min(3), descricao: z.string().optional(), status: z.string(), prioridade: z.string(), responsavel: z.string(), data_vencimento: z.string().optional() });
type FormData = z.infer<typeof schema>;

export function Tasks() {
  const { user } = useAuth();
  const [status, setStatus] = useState("");
  const [prioridade, setPrioridade] = useState("");
  const [error, setError] = useState("");
  const { data, reload } = useAsync<Task[]>(() => api.get(`/tarefas?${new URLSearchParams({ ...(status && { status }), ...(prioridade && { prioridade }) })}`), [status, prioridade]);
  const form = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { status: "Pendente", prioridade: "Media", responsavel: "Equipe BBB" } });
  async function submit(values: FormData) {
    setError("");
    try {
      await api.post("/tarefas", values);
      form.reset({ status: "Pendente", prioridade: "Media", responsavel: "Equipe BBB" });
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar a tarefa");
    }
  }
  async function complete(id: number) {
    setError("");
    try {
      await api.patch(`/tarefas/${id}/concluir`);
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel concluir a tarefa");
    }
  }
  async function deleteTask(id: number) {
    setError("");
    try {
      await api.delete(`/tarefas/${id}`);
      reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel excluir a tarefa");
    }
  }
  return (
    <>
      <PageHeader title="Tarefas" subtitle="Pendencias operacionais, prioridades e proximos passos do time." />
      {error && <Panel className="mb-4 text-red-700">{error}</Panel>}
      <CrudShell>
        <Panel>
          <h3 className="mb-4 font-semibold">Nova tarefa</h3>
          <form className="grid gap-3" onSubmit={form.handleSubmit(submit)}>
            <input className="input" placeholder="Titulo" {...form.register("titulo")} />
            <textarea className="input min-h-24" placeholder="Descricao" {...form.register("descricao")} />
            <select className="input" {...form.register("prioridade")}><option>Alta</option><option>Media</option><option>Baixa</option></select>
            <select className="input" {...form.register("status")}><option>Pendente</option><option>Em andamento</option><option>Concluida</option></select>
            <input className="input" placeholder="Responsavel" {...form.register("responsavel")} />
            <input className="input" type="date" {...form.register("data_vencimento")} />
            <button className="btn" type="submit">Criar tarefa</button>
          </form>
        </Panel>
        <Panel>
          <div className="mb-4 grid gap-3 md:grid-cols-2">
            <select className="input" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">Todos os status</option><option>Pendente</option><option>Em andamento</option><option>Concluida</option></select>
            <select className="input" value={prioridade} onChange={(e) => setPrioridade(e.target.value)}><option value="">Todas prioridades</option><option>Alta</option><option>Media</option><option>Baixa</option></select>
          </div>
          <div className="grid gap-3">
            {(data ?? []).map((task) => (
              <div key={task.id} className="subtle-card">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div><strong>{task.titulo}</strong><p className="text-sm text-slate-500">{task.responsavel} - vence {task.data_vencimento ?? "-"}</p></div>
                  <div className="flex items-center gap-2"><StatusBadge value={task.status} /><span className="badge">{task.prioridade}</span>{task.status !== "Concluida" && <button className="btn-secondary" onClick={() => complete(task.id)}>Concluir</button>}{(user?.role === "admin" || user?.role === "supervisor") && <button className="btn-secondary" onClick={() => deleteTask(task.id)}>Excluir</button>}</div>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </CrudShell>
    </>
  );
}
