export default function AuditTrail({ events = [] }) {
  return (
    <section className="panel">
      <div className="panel-title">Audit Trail</div>
      <div className="audit-list">
        {events.map((event) => (
          <div className="audit-event" key={event.event_id}>
            <time>{new Date(event.timestamp).toLocaleTimeString()}</time>
            <strong>{event.actor}</strong>
            <span>{event.action}</span>
            <p>{event.detail}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

