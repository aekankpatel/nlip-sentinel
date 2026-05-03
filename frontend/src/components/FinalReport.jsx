export default function FinalReport({ report }) {
  if (!report) return null;
  return (
    <section className="panel report-panel">
      <div className="panel-title">Final Report</div>
      <h2>{report.title}</h2>
      <p className="question">{report.research_question}</p>
      <h3>Methodology</h3>
      <p>{report.methodology}</p>
      <h3>Evidence</h3>
      <ul>{report.evidence.map((item) => <li key={item}>{item}</li>)}</ul>
      <h3>Key Result</h3>
      <p>{report.key_result}</p>
      <h3>Limitations</h3>
      <ul>{report.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
      <h3>Audit Summary</h3>
      <p>{report.audit_summary}</p>
    </section>
  );
}

