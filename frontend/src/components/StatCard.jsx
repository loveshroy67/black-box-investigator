function StatCard({ label, value, detail, tone = "neutral" }) {
  return <article className="stat-card"><span className="stat-label">{label}</span><strong className={`stat-value ${tone}`}>{value}</strong><small>{detail}</small></article>;
}

export default StatCard;
