function ErrorMessage({ message, onDismiss }) {
  if (!message) return null;
  return <div className="error-message" role="alert"><span>!</span><div><strong>Request could not be completed</strong><p>{message}</p></div>{onDismiss && <button onClick={onDismiss} aria-label="Dismiss error">×</button>}</div>;
}

export default ErrorMessage;
