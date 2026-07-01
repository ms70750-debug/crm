import { type FormEvent, useState } from "react";
import { LockKeyhole } from "lucide-react";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { api, setAuthToken } from "../lib/api";

type LoginResponse = { access_token: string; token_type: string; expires_at: string };

export function Login() {
  const [email, setEmail] = useState("admin@bbbconsig.demo");
  const [password, setPassword] = useState("BbbConsig@2026");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSaved(false);
    try {
      const data = await api.post<LoginResponse>("/auth/login", { email, password });
      setAuthToken(data.access_token);
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel autenticar");
    }
  }

  return (
    <>
      <PageHeader title="Login local" subtitle="Sessao demo para rotas protegidas, consentimentos e administracao." />
      <div className="max-w-xl">
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
            {saved && <div className="rounded-md border border-lime/40 bg-lime/10 p-3 text-sm text-lime">Sessao local ativa.</div>}
            <button className="btn" type="submit">
              <LockKeyhole size={16} /> Entrar
            </button>
          </form>
        </Panel>
      </div>
    </>
  );
}
