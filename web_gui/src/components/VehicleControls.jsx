const CONTROLS = [
  { command: 'START_VEHICLE', label: 'Start vehicle', kind: 'start' },
  { command: 'STOP_VEHICLE', label: 'Stop vehicle', kind: 'stop' },
  { command: 'ACCELERATE', label: 'Accelerate', kind: 'primary' },
  { command: 'BRAKE', label: 'Brake', kind: 'warning' },
  { command: 'STEER_LEFT', label: 'Steer left', kind: 'secondary' },
  { command: 'STEER_RIGHT', label: 'Steer right', kind: 'secondary' },
  { command: 'CENTER_STEERING', label: 'Center steering', kind: 'secondary' },
];

function isControlDisabled(command, connected, status) {
  if (!connected) return true;
  if (status === 'EMERGENCY_STOP') return true;

  if (command === 'START_VEHICLE') {
    return !['IDLE', 'STOPPED'].includes(status);
  }
  return status !== 'RUNNING';
}

export default function VehicleControls({ connected, status, onCommand }) {
  const emergencyActive = status === 'EMERGENCY_STOP';

  return (
    <section className="panel controls-panel" aria-labelledby="vehicle-controls-title">
      <div className="section-heading">
        <div>
          <p className="section-kicker">React → ROS 2</p>
          <h2 id="vehicle-controls-title">Vehicle controls</h2>
        </div>
        <span className="authority-note">State confirmed by ROS</span>
      </div>

      <div className="vehicle-button-grid">
        {CONTROLS.map((control) => (
          <button
            key={control.command}
            className={`action-button action-button--${control.kind}`}
            disabled={isControlDisabled(control.command, connected, status)}
            onClick={() => onCommand(control.command)}
          >
            {control.label}
          </button>
        ))}
        <button
          className="action-button action-button--emergency"
          disabled={!connected || emergencyActive}
          onClick={() => onCommand('EMERGENCY_STOP')}
        >
          Emergency stop
        </button>
        <button
          className="action-button action-button--reset"
          disabled={!connected}
          onClick={() => onCommand('RESET_VEHICLE')}
        >
          Reset vehicle
        </button>
      </div>
    </section>
  );
}
