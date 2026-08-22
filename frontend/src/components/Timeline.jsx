import TimelineEvent from "./TimelineEvent";

function Timeline({ events = [], compact = false }) {
  if (!events.length) return <div className="empty-state"><span className="empty-icon">◷</span><strong>No events detected</strong><p>Upload evidence to build the incident timeline.</p></div>;
  return <div className={`timeline ${compact ? "compact" : ""}`}>{events.map((event) => <TimelineEvent key={event.event_id} event={event} />)}</div>;
}

export default Timeline;
