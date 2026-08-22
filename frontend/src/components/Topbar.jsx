function Topbar({ title, incidentId, onRefresh, refreshing }) {
  return (
    <header className="top-header topbar">
      <div><p className="topbar-label">Incident response</p><h1>{title === "Incident Investigation" ? "Black Box Investigator" : title}</h1></div>
      <div className="header-actions topbar-right"><span className="connection-state connection-status"><span className="online-dot" /> Backend connected</span><span className="incident-chip incident-badge">{incidentId}</span><button className="icon-button" onClick={onRefresh} disabled={refreshing} title="Refresh incident data" aria-label="Refresh incident data">↻</button></div>
    </header>
  );
}

export default Topbar;
