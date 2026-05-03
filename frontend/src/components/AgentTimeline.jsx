import { CheckCircle2, ShieldX, AlertTriangle, Clock } from "lucide-react";

const STEPS = [
  { key: "user",     label: "User Task",          desc: (r) => r ? "Question received" : "Waiting" },
  { key: "planner",  label: "Planner Agent",      desc: (r) => r ? "Pipeline steps mapped" : "Waiting" },
  { key: "research", label: "Research Agent",     desc: (r) => r ? `${r.citations?.length ?? 0} citations collected` : "Waiting" },
  { key: "code",     label: "Code Agent",         desc: (r) => r?.blocked_reason ? "Unsafe attempt blocked" : r ? "Safe code ready" : "Waiting" },
  { key: "sentinel", label: "Sentinel Firewall",  desc: (r) => r?.blocked_reason ? r.blocked_reason.slice(0, 50) : r ? "All checks passed" : "Waiting" },
  { key: "sandbox",  label: "Sandbox Execution",  desc: (r) => r?.execution_output ? "Code executed safely" : r ? "Completed" : "Waiting" },
  { key: "verifier", label: "Verifier Agent",     desc: (r) => r ? "Claims and evidence verified" : "Waiting" },
  { key: "report",   label: "Report Agent",       desc: (r) => r?.trust_score ? `Trust score: ${r.trust_score.total}/100` : r ? "Report ready" : "Waiting" },
];

function stepState(step, result) {
  if (!result) return "idle";
  if (step.key === "sentinel" && result.blocked_reason) return "blocked";
  if (step.key === "code"     && result.blocked_reason) return "blocked";
  return "active";
}

function StepIcon({ state }) {
  if (state === "blocked") return <div className="step-icon bad"><ShieldX size={16} /></div>;
  if (state === "active")  return <div className="step-icon ok"><CheckCircle2 size={16} /></div>;
  return <div className="step-icon warn"><Clock size={16} /></div>;
}

export default function AgentTimeline({ result }) {
  return (
    <section className="panel">
      <div className="panel-title">
        <CheckCircle2 size={14} /> Agent Pipeline
      </div>
      <div className="timeline">
        {STEPS.map((step, i) => {
          const state = stepState(step, result);
          return (
            <div key={step.key} className={`timeline-step ${state !== "idle" ? state : ""}`}>
              <span className="step-num">#{i + 1}</span>
              <StepIcon state={state} />
              <strong>{step.label}</strong>
              <span className="step-status">{step.desc(result)}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
