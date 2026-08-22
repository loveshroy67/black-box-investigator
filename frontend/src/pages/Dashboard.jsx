import IncidentSummary from "../components/IncidentSummary";
import StatCard from "../components/StatCard";
import Timeline from "../components/Timeline";
import HypothesisCard from "../components/HypothesisCard";
import EvidenceUpload from "../components/EvidenceUpload";
import CorrelationView from "../components/CorrelationView";
import InvestigationGraph from "../components/InvestigationGraph";

function Dashboard({ incidentId, timeline, investigation, latestEvidence, loading, uploading, onInvestigate, onUpload }) {
  const events = timeline?.events || [];
  const hypotheses = investigation?.hypotheses || [];
  const evidenceFiles = new Set(events.map((event) => event.evidence_id).filter(Boolean)).size;
  const sourceLabel = investigation?.source === "gemini" ? "Gemini" : investigation?.source === "local" ? "Local fallback" : "Stored result";
  return <div className="page-content"><div className="page-intro"><div><p className="eyebrow">Case overview</p><h2>Stay ahead of the incident</h2><p>Correlate evidence, inspect event chronology, and review competing explanations.</p></div><span className="live-case"><span className="online-dot" /> Live case</span></div><div className="stats-grid"><StatCard label="Evidence files" value={evidenceFiles || "—"} detail={evidenceFiles ? "Tracked from event data" : "No evidence uploaded"} /><StatCard label="Events detected" value={events.length || "—"} detail="Extracted from evidence" /><StatCard label="Hypotheses" value={hypotheses.length || "—"} detail={investigation ? "Available for review" : "Awaiting investigation"} tone={hypotheses.length ? "ai" : "neutral"} /><StatCard label="Investigation status" value={investigation ? "Complete" : "Pending"} detail={investigation ? "Findings ready" : "Upload evidence first"} tone={investigation ? "success" : "warning"} /></div><IncidentSummary incidentId={incidentId} status={investigation ? "complete" : "pending"} source={investigation?.source || "stored"} onInvestigate={onInvestigate} loading={loading} /><div className="dashboard-columns"><section className="panel"><div className="panel-heading"><div><p className="section-kicker">Event sequence</p><h2>Incident timeline</h2></div><span className="panel-count">{events.length} events</span></div><Timeline events={events} compact /></section><section className="panel"><div className="panel-heading"><div><p className="section-kicker">AI-assisted reasoning</p><h2>Investigation results</h2></div>{investigation && <span className="engine-badge">{sourceLabel}</span>}</div>{hypotheses.length ? <div className="hypothesis-list">{hypotheses.slice(0, 3).map((hypothesis) => <HypothesisCard key={hypothesis.id} hypothesis={hypothesis} />)}</div> : <div className="empty-state"><span className="empty-icon">✦</span><strong>No hypotheses yet</strong><p>Upload evidence and run the investigation to generate competing explanations.</p></div>}</section></div><EvidenceUpload onUpload={onUpload} uploading={uploading} latestEvidence={latestEvidence} />{investigation && <><CorrelationView events={events} hypotheses={hypotheses} /><InvestigationGraph events={events} hypotheses={hypotheses} /></>}</div>;
}

export default Dashboard;
