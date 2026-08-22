function HypothesisCard({ hypothesis }) {
  const confidence = Math.round((hypothesis.confidence || 0) * 100);
  const tone = confidence >= 60 ? "high" : confidence >= 35 ? "medium" : "low";

  return (
    <article className={`hypothesis-card ${tone}`}>
      <div className="hypothesis-header">
        <div className="hypothesis-id">{hypothesis.id}</div>
        <div className={`confidence ${tone}`}>{confidence}%</div>
      </div>
      <h3>{hypothesis.title}</h3>
      {hypothesis.description && <p className="hypothesis-description">{hypothesis.description}</p>}
      <div className="confidence-bar">
        <span className={tone} style={{ width: `${confidence}%` }} />
      </div>
      <div className="evidence-counts">
        <span className="supporting">+ {hypothesis.supporting_evidence?.length || 0} supporting</span>
        <span className="contradicting">- {hypothesis.contradicting_evidence?.length || 0} contradicting</span>
      </div>
      {hypothesis.reasoning && (
        <div className="reasoning-block">
          <div className="reasoning-title">AI reasoning</div>
          <p>{hypothesis.reasoning}</p>
        </div>
      )}
      {hypothesis.insufficient_evidence_notes && (
        <div className="notes-block">
          <div className="notes-title">Evidence required</div>
          <p>{hypothesis.insufficient_evidence_notes}</p>
        </div>
      )}
    </article>
  );
}

export default HypothesisCard;
