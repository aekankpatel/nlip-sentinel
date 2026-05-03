import { ShieldCheck, ShieldX, AlertTriangle, Clock } from "lucide-react";

const STATUS_META = {
  approved:          { label: "Approved",      Icon: ShieldCheck,   cls: "approved" },
  blocked:           { label: "Blocked",       Icon: ShieldX,       cls: "blocked" },
  warning:           { label: "Warning",       Icon: AlertTriangle, cls: "warning" },
  requires_approval: { label: "Needs Approval",Icon: Clock,         cls: "requires_approval" },
};

export default function FirewallDecisions({ decisions = [] }) {
  if (decisions.length === 0) return (
    <section className="panel">
      <div className="panel-title"><ShieldCheck size={14} /> Firewall Decisions</div>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>Sentinel decisions will appear here after running.</p>
    </section>
  );

  return (
    <section className="panel">
      <div className="panel-title">
        <ShieldCheck size={14} /> Firewall Decisions
        <span style={{ marginLeft: "auto", color: "var(--muted)", fontWeight: 700 }}>
          {decisions.filter(d => d.status === "blocked").length} blocked ·{" "}
          {decisions.filter(d => d.status === "approved").length} approved
        </span>
      </div>
      <div className="decision-grid">
        {decisions.map((d) => {
          const meta = STATUS_META[d.status] ?? STATUS_META.approved;
          const { Icon, label, cls } = meta;
          return (
            <article key={d.decision_id} className={`decision ${cls}`}>
              <div className="decision-status">
                <Icon size={11} /> {label}
              </div>
              <strong>{d.subject}</strong>
              <p>{d.reason}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
