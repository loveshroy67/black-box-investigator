import Timeline from "../components/Timeline";

function TimelinePage({ timeline }) {
  return <div className="page-content"><div className="page-intro"><div><p className="eyebrow">Evidence chronology</p><h2>Timeline</h2><p>A chronological view of every extracted incident event.</p></div><span className="panel-count">{timeline?.total_events || 0} events</span></div><section className="panel page-panel"><div className="panel-heading"><div><p className="section-kicker">Ordered by timestamp</p><h2>Detected events</h2></div></div><Timeline events={timeline?.events || []} /></section></div>;
}

export default TimelinePage;
