import { type FormEvent, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { AuthShell } from "../components/AuthShell";

const demoModeEnabled = import.meta.env.VITE_DEMO_MODE === "true";
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
    <AuthShell title="Entrar no CRM" subtitle="Acesso administrativo para acompanhar leads, clientes, propostas e atividades da operacao consignado.">
        {demoModeEnabled && (
          <div className="mb-5 rounded-2xl border border-orange-200 bg-orange-50 p-3 text-sm font-semibold text-[var(--bbb-orange)]">
            Ambiente de demonstracao. Nao insira dados reais de clientes.
          </div>
        )}
        <div className={demoModeEnabled ? "grid gap-5 lg:grid-cols-[1fr_1.1fr]" : "mx-auto grid max-w-xl gap-5"}>
          <section>
            <form className="grid gap-4" onSubmit={submit}>
              <label className="text-sm font-semibold text-slate-700">
                E-mail
                <input className="input mt-1.5" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} />
              </label>
              <label className="text-sm font-semibold text-slate-700">
                Senha
                <input className="input mt-1.5" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} />
              </label>
              {error && <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</div>}
              <button className="btn w-full" type="submit" disabled={loading}>
                <LockKeyhole size={16} /> {loading ? "Entrando..." : "Entrar"}
              </button>
              <button className="w-fit text-sm font-bold text-[var(--bbb-blue)] hover:underline" type="button" onClick={() => navigate("/recuperar-senha")}>
                Recuperar senha
              </button>
            </form>
          </section>
          {demoModeEnabled && (
            <section className="rounded-3xl border border-[var(--bbb-line)] bg-[#f8fbff] p-4">
              <h2 className="mb-4 text-base font-extrabold text-slate-950">Usuarios demo</h2>
              <div className="grid gap-3">
                {demoUsers.map(([perfil, role]) => (
                  <button
                    className="rounded-2xl border border-[var(--bbb-line)] bg-white p-3 text-left transition hover:border-[var(--bbb-blue)] hover:shadow-[var(--bbb-shadow-panel)]"
                    key={role}
                    onClick={() => submitDemo(role)}
                    disabled={loading}
                  >
                    <strong className="block text-slate-950">{perfil}</strong>
                    <span className="block text-sm text-slate-600">Entrar em ambiente de demonstracao</span>
                  </button>
                ))}
              </div>
            </section>
          )}
        </div>
    </AuthShell>
  );
}
