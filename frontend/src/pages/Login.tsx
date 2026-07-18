import { type FormEvent, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { BrandLogo } from "../components/BrandLogo";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

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
    <>
      <div className="mx-auto max-w-5xl p-5">
        <div className="mb-6">
          <BrandLogo />
        </div>
        <PageHeader title="Login" subtitle="Acesso seguro ao CRM BBB Consig." />
        {demoModeEnabled && (
          <div className="mb-5 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700">
            Ambiente de demonstracao. Nao insira dados reais de clientes.
          </div>
        )}
        <div className={demoModeEnabled ? "grid gap-5 lg:grid-cols-[1fr_1.1fr]" : "mx-auto grid max-w-xl gap-5"}>
          <Panel>
            <form className="grid gap-3" onSubmit={submit}>
              <label className="text-sm text-slate-500">
                E-mail
                <input className="input mt-1" value={email} onChange={(event) => setEmail(event.target.value)} />
              </label>
              <label className="text-sm text-slate-500">
                Senha
                <input className="input mt-1" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
              </label>
              {error && <div className="alert-error">{error}</div>}
              <button className="btn" type="submit" disabled={loading}>
                <LockKeyhole size={16} /> {loading ? "Entrando..." : "Entrar"}
              </button>
              <button className="w-fit text-sm font-semibold text-lime hover:underline" type="button" onClick={() => navigate("/recuperar-senha")}>
                Recuperar senha
              </button>
            </form>
          </Panel>
          {demoModeEnabled && (
            <Panel>
              <img
                alt="Arte institucional BBB Consig"
                className="mb-4 aspect-[12/5] w-full rounded-md border border-line object-cover"
                src="/brand/arte-bbb-consig-horizontal.png"
              />
              <h3 className="mb-4 font-semibold">Usuarios demo</h3>
              <div className="grid gap-3">
                {demoUsers.map(([perfil, role]) => (
                  <button
                    className="rounded-md border border-line bg-[#f8fbff] p-3 text-left transition hover:border-lime/60 hover:bg-[#eef5ff]"
                    key={role}
                    onClick={() => submitDemo(role)}
                    disabled={loading}
                  >
                    <strong className="block">{perfil}</strong>
                    <span className="block text-sm text-slate-500">Entrar em ambiente de demonstracao</span>
                  </button>
                ))}
              </div>
            </Panel>
          )}
        </div>
      </div>
    </>
  );
}
