import { FileText } from "lucide-react";

export default function FinalReport({ report }) {
  if (!report) return (
    <section className="panel">
      <div className="panel-title"><FileText size={14} /> Final Report</div>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>The evidence-based report will appear here.</p>
    </section>
  );

  return (
    <section className="panel report-panel">
      <div className="panel-title"><FileText size={14} /> Final Report</div>
      <h2>{report.title}</h2>

      <div className="report-section">
        <div className="report-section-label">Research Question</div>
        <p style={{ color: "var(--text)", fontWeight: 600 }}>{report.research_question}</p>
      </div>

      <div className="report-section">
        <div className="report-section-label">Key Result</div>
        <div className="key-result">{report.key_result}</div>
      </div>

      <div className="report-section">
        <div className="report-section-label">Methodology</div>
        <p>{report.methodology}</p>
      </div>

      <div className="report-section">
        <div className="report-section-label">Evidence</div>
        <ul>
          {report.evidence.map((item, i) => (
            <li key={i}>
              {item.startsWith("http") ? (
                <a href={item} target="_blank" rel="noreferrer">{item}</a>
              ) : item}
            </li>
          ))}
        </ul>
      </div>

      <div className="report-section">
        <div className="report-section-label">Limitations</div>
        <ul>{report.limitations.map((item, i) => <li key={i}>{item}</li>)}</ul>
      </div>

      <div className="report-section">
        <div className="report-section-label">Audit Summary</div>
        <p>{report.audit_summary}</p>
      </div>
    </section>
  );
}
