export default function CodePanel({ result }) {
  return (
    <section className="panel code-panel">
      <div className="panel-title">Code Firewall</div>
      <div className="code-layout">
        <div>
          <div className="code-heading blocked-text">Unsafe attempt</div>
          <pre>{result?.unsafe_code_attempt || "Run the demo to inspect generated code."}</pre>
          <p className="blocked-text">{result?.blocked_reason}</p>
        </div>
        <div>
          <div className="code-heading approved-text">Regenerated safe code</div>
          <pre>{result?.regenerated_safe_code || "Safe code will appear here."}</pre>
        </div>
      </div>
      <div className="execution">
        <div className="code-heading">Execution output</div>
        <pre>{result?.execution_output || "Sandbox output will appear here."}</pre>
      </div>
    </section>
  );
}

