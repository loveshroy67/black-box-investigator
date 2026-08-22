function IncidentSummary({ incidentId, status, onInvestigate, loading, source }) {
  const isComplete = status === "complete";

  return (
    <section className="summary-card">
      <div className="summary-copy">
        <div className="section-kicker">Incident summary</div>
        <div className="summary-title-row">
          <div>
            <h2>{incidentId}</h2>
            <div className="incident-status-row">
              <span className={`status-indicator ${isComplete ? "complete" : "investigating"}`}>
                <span className="status-dot" />
                {isComplete ? "Investigation complete" : "Under investigation"}
              </span>
              <span className="severity-indicator"><span className="severity-dot" /> HIGH</span>
            </div>
          </div>
        </div>
        <p>Possible database and application degradation following deployment activity.</p>
        <dl className="summary-details">
          <div><dt>Severity</dt><dd className="severity-high">High</dd></div>
          <div><dt>Status</dt><dd>{isComplete ? "Complete" : "Investigating"}</dd></div>
          <div><dt>AI engine</dt><dd>{source === "gemini" ? "Gemini" : source === "local" ? "Local fallback" : source === "stored" ? "Stored result" : "Not run"}</dd></div>
          <div><dt>Scope</dt><dd>Payment service</dd></div>
        </dl>
      </div>
      <button className="primary-button" onClick={onInvestigate} disabled={loading}>
        {loading ? "Investigating..." : isComplete ? "Run investigation again" : "Investigate incident"}
        <span>→</span>
      </button>
    </section>
  );
}

export default IncidentSummary;
