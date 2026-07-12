import { type FormEvent, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

const demoUsers = [
  ["Administrador", "admin"],
  ["Supervisor", "supervisor"],
  ["Operador/Vendedor", "operador"],
  ["Parceiro", "parceiro"],
] as const;

export function Login() {
  const { demoLogin, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      const from = (location.state as { from?: string } | null)?.from ?? "/dashboard";
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel autenticar");
    } finally {
      setLoading(false);
    }
  }

  async function submitDemo(role: (typeof demoUsers)[number][1]) {
    setError("");
    setLoading(true);
    try {
      await demoLogin(role);
      const from = (location.state as { from?: string } | null)?.from ?? "/dashboard";
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel autenticar em demo");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="mx-auto max-w-5xl p-5">
      <PageHeader title="Login local" subtitle="Sessao demo para rotas protegidas, consentimentos e administracao." />
      <div className="mb-5 rounded-md border border-lime/40 bg-lime/10 p-3 text-sm text-lime">
        Ambiente de demonstracao. Nao insira dados reais de clientes.
      </div>
      <div className="grid gap-5 lg:grid-cols-[1fr_1.1fr]">
        <Panel>
          <form className="grid gap-3" onSubmit={submit}>
            <label className="text-sm text-slate-400">
              E-mail
              <input className="input mt-1" value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label className="text-sm text-slate-400">
              Senha
              <input className="input mt-1" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            {error && <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
            <button className="btn" type="submit" disabled={loading}>
              <LockKeyhole size={16} /> {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
        </Panel>
        <Panel>
          <h3 className="mb-4 font-semibold">Usuarios demo</h3>
          <div className="grid gap-3">
            {demoUsers.map(([perfil, role]) => (
              <button
                className="rounded-md border border-line bg-white/5 p-3 text-left transition hover:border-lime/60"
                key={role}
                onClick={() => submitDemo(role)}
                disabled={loading}
              >
                <strong className="block">{perfil}</strong>
                <span className="block text-sm text-slate-400">Entrar em ambiente de demonstracao</span>
              </button>
            ))}
          </div>
        </Panel>
      </div>
      </div>
    </>
  );
}
