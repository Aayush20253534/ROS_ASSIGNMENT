import ConnectionStatus from './components/ConnectionStatus.jsx';
import EventLog from './components/EventLog.jsx';
import RecorderControls from './components/RecorderControls.jsx';
import TelemetryCard from './components/TelemetryCard.jsx';
import VehicleControls from './components/VehicleControls.jsx';
import { useRosBridge } from './hooks/useRosBridge.js';
import { ROSBRIDGE_URL, ROS_TOPICS } from './services/rosTopics.js';
import './App.css';

function formatValue(value, decimals = 1) {
  return value === null ? '--' : value.toFixed(decimals);
}

function displayStatus(status) {
  return status === 'UNKNOWN' ? 'Waiting for ROS' : status.replaceAll('_', ' ');
}

export default function App() {
  const ros = useRosBridge();
  const connected = ros.connectionStatus === 'connected';
  const statusClass = ros.vehicleStatus.toLowerCase().replaceAll('_', '-');

  return (
    <main className="app-shell">
      <div className="dashboard">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">Simulated self-driving car</p>
            <h1>ROS 2 Vehicle Console</h1>
            <p className="subtitle">
              Real topic flow from React controls to an authoritative ROS 2 simulator.
            </p>
          </div>
          <ConnectionStatus status={ros.connectionStatus} />
        </header>

        <section className={`vehicle-status vehicle-status--${statusClass}`}>
          <div>
            <span className="metric-label">ROS-confirmed vehicle state</span>
            <strong>{displayStatus(ros.vehicleStatus)}</strong>
          </div>
          <div className="last-command">
            <span>Last GUI command</span>
            <strong>{ros.lastAction}</strong>
          </div>
        </section>

        <section className="telemetry-grid" aria-label="Live vehicle telemetry">
          <TelemetryCard
            label="Temperature"
            value={formatValue(ros.telemetry.temperature, 2)}
            unit="°C"
            detail={ROS_TOPICS.temperature.name}
            accent="cyan"
          />
          <TelemetryCard
            label="Speed"
            value={formatValue(ros.telemetry.speed)}
            unit="km/h"
            detail={ROS_TOPICS.sdcSpeed.name}
            accent="blue"
          />
          <TelemetryCard
            label="Steering"
            value={formatValue(ros.telemetry.steering)}
            unit="°"
            detail={ROS_TOPICS.sdcSteering.name}
            accent="violet"
          />
          <TelemetryCard
            label="Battery"
            value={formatValue(ros.telemetry.battery)}
            unit="%"
            detail={ROS_TOPICS.sdcBattery.name}
            accent="green"
          />
        </section>

        <VehicleControls
          connected={connected}
          status={ros.vehicleStatus}
          onCommand={ros.sendVehicleCommand}
        />

        <div className="lower-grid">
          <RecorderControls
            connected={connected}
            recorderState={ros.recorderState}
            recordedCount={ros.recordedCount}
            messageCount={ros.messageCount}
            sampleCount={ros.sampleCount}
            onTestMessage={ros.sendTestMessage}
            onRecorderCommand={ros.sendRecorderCommand}
          />
          <EventLog events={ros.events} onClear={ros.clearEvents} />
        </div>

        <footer className="connection-note">
          <span>rosbridge</span><code>{ROSBRIDGE_URL}</code>
          <span>command topic</span><code>{ROS_TOPICS.sdcCommand.name}</code>
          <span>events topic</span><code>{ROS_TOPICS.sdcEvents.name}</code>
        </footer>
      </div>
    </main>
  );
}
