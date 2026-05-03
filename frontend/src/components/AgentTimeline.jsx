import { CheckCircle2, CircleAlert, ShieldX } from "lucide-react";

const steps = [
  "User Task",
  "Planner Agent",
  "Research Agent",
  "Code Agent",
  "Sentinel Firewall",
  "Sandbox Execution",
  "Verifier Agent",
  "Report Agent",
];

function iconFor(step, result) {
  if (step === "Sentinel Firewall" && result?.blocked_reason) return <ShieldX size={18} />;
  if (step === "Sandbox Execution") return <CircleAlert size={18} />;
  return <CheckCircle2 size={18} />;
}

export default function AgentTimeline({ result }) {
  return (
    <section className="panel timeline-panel">
      <div className="panel-title">Agent Timeline</div>
      <div className="timeline">
        {steps.map((step) => (
          <div className="timeline-step" key={step}>
            <div className="timeline-icon">{iconFor(step, result)}</div>
            <div>
              <strong>{step}</strong>
              <span>
                {step === "Sentinel Firewall" && result?.blocked_reason
                  ? "Blocked unsafe attempt, approved safe retry"
                  : "Completed"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

