export default function ConnectionStatus({ status }) {
  const labels = {
    connected: 'Connected to ROS 2',
    disconnected: 'Disconnected',
    error: 'Connection error',
  };

  return (
    <span className={`status-badge status-badge--${status}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      {labels[status] || labels.disconnected}
    </span>
  );
}
