export default function RecorderControls({
  connected,
  recorderState,
  recordedCount,
  messageCount,
  sampleCount,
  onTestMessage,
  onRecorderCommand,
}) {
  const isRecording = recorderState === 'recording';

  return (
    <section className="panel recorder-panel" aria-labelledby="recorder-title">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Telemetry CSV</p>
          <h2 id="recorder-title">Recording</h2>
        </div>
        <strong className={`recorder-pill recorder-pill--${recorderState}`}>
          {isRecording ? 'Recording' : 'Idle'}
        </strong>
      </div>

      <div className="recorder-stats">
        <div><strong>{recordedCount.toLocaleString()}</strong><span>CSV rows</span></div>
        <div><strong>{sampleCount.toLocaleString()}</strong><span>Temperature samples</span></div>
        <div><strong>{messageCount.toLocaleString()}</strong><span>Test events</span></div>
      </div>

      <div className="recorder-buttons">
        <button
          className="action-button action-button--primary"
          disabled={!connected}
          onClick={onTestMessage}
        >
          Send test message
        </button>
        <button
          className="action-button action-button--start"
          disabled={!connected || isRecording}
          onClick={() => onRecorderCommand('start', 'Recording started')}
        >
          Start recording
        </button>
        <button
          className="action-button action-button--stop"
          disabled={!connected || !isRecording}
          onClick={() => onRecorderCommand('stop', 'Recording stopped')}
        >
          Stop recording
        </button>
        <button
          className="action-button action-button--reset"
          disabled={!connected}
          onClick={() => onRecorderCommand('reset', 'CSV reset')}
        >
          Reset CSV
        </button>
      </div>
    </section>
  );
}
