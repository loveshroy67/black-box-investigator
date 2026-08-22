function InvestigationGraph({ events = [], hypotheses = [] }) {
  const relationshipLimit = 5;
  const limitedHypotheses = hypotheses.map((hypothesis) => ({
    ...hypothesis,
    supporting_evidence: (hypothesis.supporting_evidence || []).slice(0, relationshipLimit),
    contradicting_evidence: (hypothesis.contradicting_evidence || []).slice(0, relationshipLimit),
  }));
  const connectedIds = new Set(
    limitedHypotheses.flatMap((hypothesis) => [
      ...(hypothesis.supporting_evidence || []),
      ...(hypothesis.contradicting_evidence || []),
    ])
  );
  const graphEvents = events.filter((event) => connectedIds.has(event.event_id));

  return (
    <section className="panel investigation-graph">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">Relationship map</p>
          <h2>Investigation graph</h2>
        </div>
        <span className="panel-count">{graphEvents.length} linked events</span>
      </div>
      <div className="graph-layout">
        <div className="graph-column">
          <div className="graph-column-title">Events</div>
          <div className="graph-events">
            {graphEvents.map((event) => (
              <div className="graph-event" key={event.event_id}>
                <span className="graph-node event-node" />
                <div>
                  <strong>{event.title || event.message || event.description || event.event || event.event_id}</strong>
                  <small>{event.type ? event.type.toUpperCase() : "EVENT"} · {event.event_id}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="graph-connections" aria-hidden="true">
          {graphEvents.map((event) => {
            const relationships = limitedHypotheses.flatMap((hypothesis) => [
              ...(hypothesis.supporting_evidence || []).includes(event.event_id) ? [{ type: "supporting", id: hypothesis.id }] : [],
              ...(hypothesis.contradicting_evidence || []).includes(event.event_id) ? [{ type: "contradicting", id: hypothesis.id }] : [],
            ]);
            return <div className="connection-row" key={event.event_id}>{relationships.map((relationship) => <div className={`connection-line ${relationship.type === "supporting" ? "supporting-line" : "contradicting-line"}`} key={`${event.event_id}-${relationship.id}-${relationship.type}`}><span className="connection-arrow" /><small>{relationship.type === "supporting" ? "supports" : "contradicts"} {relationship.id}</small></div>)}</div>;
          })}
        </div>
        <div className="graph-column">
          <div className="graph-column-title">Hypotheses</div>
          <div className="graph-hypotheses">
            {hypotheses.map((hypothesis) => {
              const confidence = Math.round((hypothesis.confidence || 0) * 100);
              return <div className="graph-hypothesis" key={hypothesis.id}><span className="graph-node hypothesis-node" /><div><div className="graph-hypothesis-header"><span>{hypothesis.id}</span><strong>{confidence}%</strong></div><h3>{hypothesis.title}</h3><div className="graph-evidence-summary"><span className="support-count">+ {hypothesis.supporting_evidence?.length || 0}</span><span className="contradict-count">- {hypothesis.contradicting_evidence?.length || 0}</span></div></div></div>;
            })}
          </div>
        </div>
      </div>
      <div className="graph-legend"><span><i className="legend-support" /> Supporting evidence</span><span><i className="legend-contradict" /> Contradicting evidence</span></div>
    </section>
  );
}

export default InvestigationGraph;
