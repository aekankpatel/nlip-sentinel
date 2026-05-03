import { ListChecks } from "lucide-react";

export default function AuditTrail({ events = [] }) {
  if (events.length === 0) return (
    <section className="panel">
      <div className="panel-title"><ListChecks size={14} /> Audit Trail</div>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>Every agent action will be logged here.</p>
    </section>
  );

  return (
    <section className="panel">
      <div className="panel-title">
        <ListChecks size={14} /> Audit Trail
        <span style={{ marginLeft: "auto", color: "var(--muted)", fontWeight: 700 }}>
          {events.length} events
        </span>
      </div>
      <div className="audit-list">
        {events.map((event) => (
          <div className="audit-event" key={event.event_id}>
            <div className="audit-time">
              {new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </div>
            <div className="audit-body">
              <span className="audit-actor">{event.actor}</span>
              <span className="audit-action">{event.action}</span>
              <div className="audit-detail">{event.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
