function LoadingState({ label = "Loading investigation data" }) {
  return <div className="loading-state"><span className="spinner" /><span>{label}</span></div>;
}

export default LoadingState;
