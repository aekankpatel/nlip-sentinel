const statusLabel = {
  approved: "Approved",
  warning: "Warning",
  requires_approval: "Needs approval",
  blocked: "Blocked",
};

export default function FirewallDecisions({ decisions = [] }) {
  return (
    <section className="panel">
      <div className="panel-title">Firewall Decisions</div>
      <div className="decision-grid">
        {decisions.map((decision) => (
          <article className={`decision ${decision.status}`} key={decision.decision_id}>
            <div className="decision-status">{statusLabel[decision.status] || decision.status}</div>
            <strong>{decision.subject}</strong>
            <p>{decision.reason}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

