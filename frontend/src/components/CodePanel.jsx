import { ShieldX, ShieldCheck, Terminal } from "lucide-react";

export default function CodePanel({ result }) {
  const placeholder = "Run the demo to inspect generated code.";

  return (
    <section className="panel">
      <div className="panel-title"><Terminal size={14} /> Code Firewall</div>

      <div className="code-layout">
        <div>
          <div className="code-heading blocked-text">
            <ShieldX size={13} /> Unsafe attempt
          </div>
          <pre>{result?.unsafe_code_attempt ?? placeholder}</pre>
          {result?.blocked_reason && (
            <div className="blocked-banner">
              <ShieldX size={13} /> {result.blocked_reason}
            </div>
          )}
        </div>

        <div>
          <div className="code-heading approved-text">
            <ShieldCheck size={13} /> Regenerated safe code
          </div>
          <pre>{result?.regenerated_safe_code ?? "Safe code will appear here."}</pre>
        </div>
      </div>

      <div className="execution">
        <div className="code-heading neutral">
          <Terminal size={13} /> Sandbox execution output
        </div>
        <pre>{result?.execution_output ?? "Sandbox output will appear here."}</pre>
      </div>
    </section>
  );
}
