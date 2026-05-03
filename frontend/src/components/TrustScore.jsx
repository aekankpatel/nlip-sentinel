function scoreColor(total) {
  if (total >= 90) return "var(--teal)";
  if (total >= 80) return "var(--green)";
  if (total >= 70) return "var(--amber)";
  return "var(--red)";
}

function Gauge({ total }) {
  const R = 50;
  const C = 2 * Math.PI * R;
  const pct = Math.min(total, 100) / 100;
  const color = scoreColor(total);

  return (
    <div className="trust-gauge">
      <svg width="114" height="114" viewBox="0 0 114 114">
        {/* track */}
        <circle cx="57" cy="57" r={R} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
        {/* fill */}
        <circle
          cx="57" cy="57" r={R}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={`${C * pct} ${C * (1 - pct)}`}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: "stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1)" }}
        />
      </svg>
      <div className="trust-gauge-label">
        <span className="big" style={{ color }}>{total}</span>
        <span className="small">/100</span>
      </div>
    </div>
  );
}

export default function TrustScore({ score }) {
  if (!score) return (
    <section className="panel">
      <div className="panel-title">Trust Score</div>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>Run the demo to compute a trust score.</p>
    </section>
  );

  const items = [
    ["Schema",        score.schema_validity,       20],
    ["Permissions",   score.permission_compliance, 20],
    ["Tool safety",   score.tool_safety,           20],
    ["Evidence",      score.evidence_support,      20],
    ["Reproducibility", score.reproducibility,     20],
  ];

  const color = scoreColor(score.total);

  return (
    <section className="panel">
      <div className="panel-title">Trust Score</div>
      <div className="trust-layout">
        <Gauge total={score.total} />
        <div className="score-bars">
          {items.map(([label, value, max]) => (
            <div className="score-row" key={label}>
              <span>{label}</span>
              <div className="bar">
                <div style={{ width: `${(value / max) * 100}%`, background: value === max ? "var(--teal)" : color }} />
              </div>
              <b style={{ color: value === max ? "var(--text)" : color }}>{value}</b>
            </div>
          ))}
        </div>
      </div>
      {score.notes?.length > 0 && (
        <div className="score-notes">
          {score.notes.slice(0, 4).map((note) => (
            <div className="score-note" key={note}>{note}</div>
          ))}
        </div>
      )}
    </section>
  );
}
