function CorrelationView({ events = [], hypotheses = [] }) {
  const eventById = new Map(events.map((event) => [event.event_id, event]));

  const getEvent = (eventId) => eventById.get(eventId);
  const eventLabel = (event, eventId) => event?.title || event?.message || event?.description || event?.event || eventId;

  const renderEvidence = (eventIds, tone) => (
    <div className={`correlation-group ${tone}`}>
      <div className="correlation-group-header">
        <strong>{tone === "supporting" ? "Supporting evidence" : "Contradicting evidence"}</strong>
        <span>{eventIds.length}</span>
      </div>
      <div className="correlation-events">
        {eventIds.map((eventId) => {
          const event = getEvent(eventId);
          return (
            <div className="correlation-event" key={eventId}>
              <span className="correlation-dot" />
              <div>
                <strong>{eventLabel(event, eventId)}</strong>
                <small>{event?.type ? event.type.toUpperCase() : "EVENT"} · {eventId}</small>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <section className="panel correlation-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">Evidence mapping</p>
          <h2>Incident correlation</h2>
        </div>
        <span className="panel-count">{hypotheses.length} hypotheses</span>
      </div>
      <div className="correlation-list">
        {hypotheses.map((hypothesis) => {
          const supporting = hypothesis.supporting_evidence || [];
          const contradicting = hypothesis.contradicting_evidence || [];
          const confidence = Math.round((hypothesis.confidence || 0) * 100);
          const tone = confidence >= 60 ? "high" : confidence >= 35 ? "medium" : "low";

          return (
            <article className="correlation-card" key={hypothesis.id}>
              <div className="correlation-card-header">
                <div>
                  <span className="hypothesis-id">{hypothesis.id}</span>
                  <h3>{hypothesis.title}</h3>
                </div>
                <span className={`confidence ${tone}`}>{confidence}%</span>
              </div>
              <div className="correlation-track"><span className={tone} style={{ width: `${confidence}%` }} /></div>
              {supporting.length > 0 && renderEvidence(supporting, "supporting")}
              {contradicting.length > 0 && renderEvidence(contradicting, "contradicting")}
              <div className="reasoning-block">
                <strong>Why this matters</strong>
                <p>{hypothesis.reasoning || "No reasoning provided."}</p>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default CorrelationView;
