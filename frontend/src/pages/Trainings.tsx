import { CheckSquare, FileText, PlayCircle } from "lucide-react";
import { Panel } from "../components/CrudShell";
import { PageHeader } from "../components/PageHeader";

const lessons = ["Como qualificar lead INSS", "Simulacao FGTS com abordagem segura", "Esteira: captacao, enriquecimento, simulacao e contrato", "Boas praticas de atendimento consultivo"];
const checklist = ["Configurar usuarios ficticios", "Cadastrar primeiras fontes de lead", "Revisar modelos de WhatsApp", "Treinar operadores no pipeline", "Validar relatorios do dashboard"];
const prompts = ["Crie uma abordagem curta para lead INSS frio.", "Resuma as pendencias deste cliente em tom consultivo.", "Transforme estas observacoes em proximas tarefas."];

export function Trainings() {
  return (
    <>
      <PageHeader title="Treinamentos" subtitle="Aulas, checklist de implantacao, prompts e base de conhecimento inicial." />
      <div className="grid gap-5 lg:grid-cols-3">
        <Panel><h3 className="mb-4 flex gap-2 font-semibold"><PlayCircle size={18} /> Aulas</h3><List items={lessons} /></Panel>
        <Panel><h3 className="mb-4 flex gap-2 font-semibold"><CheckSquare size={18} /> Checklist</h3><List items={checklist} /></Panel>
        <Panel><h3 className="mb-4 flex gap-2 font-semibold"><FileText size={18} /> Prompts</h3><List items={prompts} /></Panel>
      </div>
      <Panel className="mt-5">
        <h3 className="mb-3 font-semibold">Base de conhecimento</h3>
        <p className="text-sm leading-6 text-slate-300">A primeira versao organiza a operacao em quatro etapas: captacao, enriquecimento, simulacao e contrato. O objetivo e reduzir esquecimentos, padronizar atendimento e manter toda acao registrada antes de qualquer integracao real.</p>
      </Panel>
    </>
  );
}

function List({ items }: { items: string[] }) {
  return <div className="grid gap-3">{items.map((item) => <div className="rounded-md border border-line bg-white/5 p-3 text-sm" key={item}>{item}</div>)}</div>;
}
