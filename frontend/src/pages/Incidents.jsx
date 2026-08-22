function Incidents({ incidentId, investigation, timeline }) {
  const isComplete = Boolean(investigation);
  const eventCount = timeline?.total_events || 0;

  return (
    <div className="page-content">
      <div className="page-intro">
        <div>
          <p className="eyebrow">Case management</p>
          <h2>Incidents</h2>
          <p>Active cases currently available in the investigation workspace.</p>
        </div>
      </div>
      <section className="panel incident-list">
        <div className="incident-row">
          <div className="incident-leading">
            <span className="severity-marker" />
            <div>
              <strong>{incidentId}</strong>
              <p>Possible database and application degradation following deployment activity.</p>
            </div>
          </div>
          <div className="incident-row-meta">
            <span className={`status-pill ${isComplete ? "success" : "warning"}`}>
              {isComplete ? "Complete" : "Under investigation"}
            </span>
            <span>{eventCount} events</span>
            {investigation && <span>{investigation.hypotheses?.length || 0} hypotheses</span>}
          </div>
        </div>
      </section>
    </div>
  );
}

export default Incidents;
