import { type FormEvent, useState } from "react";
import { MailCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";
import { api } from "../lib/api";

type PasswordRecoveryResponse = {
  ok: boolean;
  message: string;
};

export function PasswordRecoveryRequest() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);
    try {
      const response = await api.post<PasswordRecoveryResponse>("/auth/password-recovery/request", { email });
      setMessage(response.message);
    } catch {
      setError("Nao foi possivel preparar a recuperacao agora. Aguarde e tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl p-5">
      <PageHeader title="Recuperar senha" subtitle="Prepare um link seguro para redefinir o acesso ao CRM BBB Consig." />
      <Panel>
        <form className="grid gap-3" onSubmit={submit}>
          <label className="text-sm text-slate-400">
            E-mail
            <input className="input mt-1" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          {message && <div className="rounded-md border border-lime/40 bg-lime/10 p-3 text-sm text-lime">{message}</div>}
          {error && <div className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
          <button className="btn" type="submit" disabled={loading}>
            <MailCheck size={16} /> {loading ? "Preparando..." : "Preparar recuperacao"}
          </button>
          <button className="w-fit text-sm text-slate-400 hover:text-lime" type="button" onClick={() => navigate("/login")}>
            Voltar ao login
          </button>
        </form>
      </Panel>
    </div>
  );
}
