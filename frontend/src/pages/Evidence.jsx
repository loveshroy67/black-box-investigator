import EvidenceUpload from "../components/EvidenceUpload";

function Evidence({ latestEvidence, onUpload, uploading }) {
  const eventCount = latestEvidence?.events?.length || 0;

  return (
    <div className="page-content">
      <div className="page-intro">
        <div>
          <p className="eyebrow">Collection</p>
          <h2>Evidence</h2>
          <p>Upload the artifacts that will anchor this investigation.</p>
        </div>
      </div>
      <EvidenceUpload onUpload={onUpload} uploading={uploading} latestEvidence={latestEvidence} />
      {latestEvidence ? (
        <section className="panel evidence-detail">
          <div className="panel-heading">
            <div>
              <p className="section-kicker">Latest artifact</p>
              <h2>{latestEvidence.filename}</h2>
            </div>
            <span className="status-pill success">{latestEvidence.status || "processed"}</span>
          </div>
          <dl className="evidence-grid">
            <div><dt>Evidence ID</dt><dd>{latestEvidence.evidence_id || "—"}</dd></div>
            <div><dt>File type</dt><dd>{latestEvidence.file_type || "—"}</dd></div>
            <div><dt>Extracted events</dt><dd>{eventCount}</dd></div>
            <div><dt>Processing</dt><dd>{eventCount > 0 ? "Events extracted" : "No events detected"}</dd></div>
          </dl>
        </section>
      ) : (
        <div className="panel empty-state">
          <span className="empty-icon">⌁</span>
          <strong>No evidence uploaded</strong>
          <p>Upload a log, trace, or report to begin the investigation.</p>
        </div>
      )}
    </div>
  );
}

export default Evidence;
