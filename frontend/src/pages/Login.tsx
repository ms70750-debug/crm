import { type FormEvent, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

const demoUsers = [
  ["Administrador", "admin@bbbconsig.demo", "BbbConsig@2026"],
  ["Supervisor", "supervisor@bbbconsig.demo", "Supervisor@2026"],
  ["Operador/Vendedor", "operador@bbbconsig.demo", "Operador@2026"],
  ["Parceiro", "parceiro@bbbconsig.demo", "Parceiro@2026"],
];

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("admin@bbbconsig.demo");
  const [password, setPassword] = useState("BbbConsig@2026");
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

  return (
    <>
      <div className="mx-auto max-w-5xl p-5">
      <PageHeader title="Login local" subtitle="Sessao demo para rotas protegidas, consentimentos e administracao." />
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
            {demoUsers.map(([perfil, userEmail, userPassword]) => (
              <button
                className="rounded-md border border-line bg-white/5 p-3 text-left transition hover:border-lime/60"
                key={userEmail}
                onClick={() => {
                  setEmail(userEmail);
                  setPassword(userPassword);
                }}
              >
                <strong className="block">{perfil}</strong>
                <span className="block text-sm text-slate-400">{userEmail}</span>
                <span className="block text-xs text-slate-500">{userPassword}</span>
              </button>
            ))}
          </div>
        </Panel>
      </div>
      </div>
    </>
  );
}
