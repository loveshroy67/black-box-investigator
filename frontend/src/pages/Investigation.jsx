import HypothesisCard from "../components/HypothesisCard";

function Investigation({ investigation, onInvestigate, loading }) {
  const hypotheses = investigation?.hypotheses || [];
  const sourceLabel = investigation?.source === "gemini"
    ? "AI analysis"
    : investigation?.source === "openrouter"
      ? "OpenRouter analysis"
    : investigation?.source === "local"
      ? "Local analysis"
      : "Stored analysis";
  const sourceTone = investigation?.source === "gemini" ? "success" : investigation?.source === "openrouter" ? "ai" : "warning";

  return <div className="page-content"><div className="page-intro"><div><p className="eyebrow">Analyst review</p><h2>Investigation</h2><p>Compare evidence-backed hypotheses without assuming a definitive root cause.</p></div><button className="primary-button" onClick={onInvestigate} disabled={loading}>{loading ? "Investigating..." : "Run investigation"}<span>→</span></button></div>{investigation && <section className="result-banner"><span className="online-dot" /><div><strong>Investigation complete</strong><p>{investigation.source === "gemini" ? "Gemini analysis completed." : investigation.source === "openrouter" ? "OpenRouter analysis completed." : investigation.source === "local" ? "Gemini and OpenRouter unavailable; local fallback completed." : "Loaded stored investigation results."}</p></div><span className={`status-pill ${sourceTone}`}>{sourceLabel}</span></section>}<section className="hypothesis-list full-list">{hypotheses.length ? hypotheses.map((hypothesis) => <HypothesisCard key={hypothesis.id} hypothesis={hypothesis} />) : <div className="panel empty-state"><span className="empty-icon">✦</span><strong>No investigation results</strong><p>Upload evidence, then run the investigation.</p></div>}</section></div>;
}

export default Investigation;
