export default function TelemetryCard({ label, value, unit, detail, accent }) {
  return (
    <article className={`telemetry-card telemetry-card--${accent}`}>
      <span className="metric-label">{label}</span>
      <strong className="telemetry-value">
        {value}
        <span>{unit}</span>
      </strong>
      <span className="metric-detail">{detail}</span>
    </article>
  );
}
