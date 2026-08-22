import { useRef, useState } from "react";

function EvidenceUpload({ onUpload, uploading, latestEvidence }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const handleFiles = (files) => {
    const file = files?.[0];
    if (file) onUpload(file);
  };

  return (
    <section
      className={`upload-panel ${dragging ? "dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
    >
      <div className="upload-icon">↑</div>
      <div className="upload-content">
        <p className="section-kicker">Evidence ingestion</p>
        <h3>{uploading ? "Processing evidence..." : "Upload incident evidence"}</h3>
        <p>Upload logs, traces, reports, or other incident evidence for analysis.</p>
        {latestEvidence && (
          <div className="uploaded-file">
            <span className="file-icon">▣</span>
            <div>
              <strong>{latestEvidence.filename}</strong>
              <small>{latestEvidence.file_type || "Evidence"} · {latestEvidence.status || "processed"}</small>
            </div>
          </div>
        )}
      </div>
      <button className="secondary-button" onClick={() => inputRef.current?.click()} disabled={uploading}>
        {uploading ? "Processing..." : "Browse files"}
      </button>
      <input ref={inputRef} type="file" onChange={(event) => handleFiles(event.target.files)} disabled={uploading} hidden />
    </section>
  );
}

export default EvidenceUpload;
