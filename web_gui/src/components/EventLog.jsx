export default function EventLog({ events, onClear }) {
  return (
    <section className="panel event-panel" aria-labelledby="event-log-title">
      <div className="section-heading">
        <div>
          <p className="section-kicker">ROS event stream</p>
          <h2 id="event-log-title">Live event log</h2>
        </div>
        <button className="clear-button" onClick={onClear} disabled={!events.length}>
          Clear logs
        </button>
      </div>

      <div className="event-list" aria-live="polite">
        {events.length === 0 ? (
          <p className="empty-log">Vehicle and recorder events will appear here.</p>
        ) : (
          events.map((event) => (
            <div className="event-row" key={event.id}>
              <time>{event.timestamp}</time>
              <span>{event.message}</span>
            </div>
          ))
        )}
      </div>
      <p className="event-limit">Showing the latest {events.length} of at most 50 events.</p>
    </section>
  );
}
