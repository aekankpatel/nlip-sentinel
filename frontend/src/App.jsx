import { useState } from "react";
import { Activity, Play, ShieldCheck } from "lucide-react";
import { runWorkflow } from "./api.js";
import AgentTimeline from "./components/AgentTimeline.jsx";
import FirewallDecisions from "./components/FirewallDecisions.jsx";
import TrustScore from "./components/TrustScore.jsx";
import CodePanel from "./components/CodePanel.jsx";
import FinalReport from "./components/FinalReport.jsx";
import AuditTrail from "./components/AuditTrail.jsx";

const defaultQuestion =
  "Research whether oil price changes meaningfully affect airline stock returns, write Python analysis code, run it safely, and produce a final evidence-based report.";

export default function App() {
  const [question, setQuestion] = useState(defaultQuestion);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      setResult(await runWorkflow(question));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><ShieldCheck size={16} /> AG2 Multi-Agent Trust Layer</div>
          <h1>NLIP Sentinel</h1>
          <p className="subtitle">Trust firewall for AG2 multi-agent workflows</p>
          <p className="description">
            Validate messages, enforce permissions, block unsafe tools, verify evidence, and audit every agent decision.
          </p>
          <div className="privacy-badge">Live trust telemetry for every agent message, tool call, and claim.</div>
        </div>
        <div className="run-box">
          <label htmlFor="question">Demo scenario</label>
          <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button onClick={handleRun} disabled={loading}>
            {loading ? <Activity size={18} className="spin" /> : <Play size={18} />}
            {loading ? "Running Sentinel..." : "Run Sentinel Demo"}
          </button>
          {error && <p className="error">{error}</p>}
        </div>
      </section>

      <section className="dashboard">
        <div className="left-stack">
          <AgentTimeline result={result} />
          <FirewallDecisions decisions={result?.firewall_decisions || []} />
          <CodePanel result={result} />
        </div>
        <div className="right-stack">
          <TrustScore score={result?.trust_score} />
          <FinalReport report={result?.final_report} />
          <AuditTrail events={result?.audit_events || []} />
        </div>
      </section>
    </main>
  );
}
