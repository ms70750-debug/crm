import { type FormEvent, useState } from "react";
import { MailCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { AuthShell } from "../components/AuthShell";
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
    <AuthShell title="Recuperar senha" subtitle="Prepare um link seguro para redefinir o acesso ao CRM BBB Consig.">
        <form className="grid gap-4" onSubmit={submit}>
          <label className="text-sm font-semibold text-slate-700">
            E-mail
            <input className="input mt-1.5" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          {message && <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">{message}</div>}
          {error && <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</div>}
          <button className="btn w-full" type="submit" disabled={loading}>
            <MailCheck size={16} /> {loading ? "Preparando..." : "Preparar recuperacao"}
          </button>
          <button className="w-fit text-sm font-bold text-slate-600 hover:text-[var(--bbb-blue)]" type="button" onClick={() => navigate("/login")}>
            Voltar ao login
          </button>
        </form>
    </AuthShell>
  );
}
