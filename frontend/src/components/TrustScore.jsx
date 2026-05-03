export default function TrustScore({ score }) {
  if (!score) return null;
  const items = [
    ["Schema", score.schema_validity],
    ["Permissions", score.permission_compliance],
    ["Tool safety", score.tool_safety],
    ["Evidence", score.evidence_support],
    ["Reproducibility", score.reproducibility],
  ];
  return (
    <section className="panel trust-panel">
      <div>
        <div className="panel-title">Trust Score</div>
        <div className="score">{score.total}<span>/100</span></div>
      </div>
      <div className="score-bars">
        {items.map(([label, value]) => (
          <div className="score-row" key={label}>
            <span>{label}</span>
            <div className="bar"><div style={{ width: `${(value / 20) * 100}%` }} /></div>
            <b>{value}</b>
          </div>
        ))}
        {score.notes?.length > 0 && (
          <div className="score-notes">
            {score.notes.slice(0, 3).map((note) => (
              <p key={note}>{note}</p>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
