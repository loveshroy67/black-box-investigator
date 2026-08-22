function TimelineEvent({ event }) {
  const type = (event.type || "other").toLowerCase();
  const severity = (event.severity || "info").toLowerCase();
  const severityClass = {
    critical: "critical",
    high: "high",
    medium: "medium",
    low: "low",
    info: "info",
  }[severity] || "info";
  const typeClass = {
    deployment: "deployment",
    database: "database",
    application: "application",
    infrastructure: "infrastructure",
    other: "other",
  }[type] || "other";
  const title = event.title || event.message || event.description || event.event || "Incident event";

  return (
    <article className={`timeline-event ${severityClass}`}>
      <div className="timeline-marker">
        <span />
      </div>
      <div className="timeline-event-content">
        <div className="timeline-event-top">
          <span className="event-time">
            {event.timestamp ? new Date(event.timestamp).toLocaleString() : "Unknown time"}
          </span>
          <span className={`event-type ${typeClass}`}>{type.toUpperCase()}</span>
          <span className={`event-severity ${severityClass}`}>{severity.toUpperCase()}</span>
        </div>
        <h3>{title}</h3>
        {event.description && <p>{event.description}</p>}
        {event.message && event.message !== event.title && event.message !== event.description && <p>{event.message}</p>}
        {event.source && <div className="event-source">Source: {event.source}</div>}
        {event.event_id && <div className="event-id">Event ID: {event.event_id}</div>}
      </div>
    </article>
  );
}

export default TimelineEvent;
