import { useEffect, useRef, useState } from 'react';
import ROSLIB from 'roslib';
import './App.css';

// Keep these strings identical to gui_interface/topics.py. JavaScript cannot
// import the Python constants, so TOPICS.md documents the shared contract.
const TOPICS = {
  buttonPress: '/button_press',
  temperature: '/sensor/temperature',
  recorderCommand: '/recorder/command',
  recorderStatus: '/recorder/status',
};

function defaultRosbridgeUrl() {
  if (typeof window !== 'undefined' && window.location) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}/rosbridge`;
  }
  return 'ws://localhost:9090';
}

const ROSBRIDGE_URL =
  import.meta.env.VITE_ROSBRIDGE_URL || defaultRosbridgeUrl();

function ConnectionBadge({ status }) {
  const labels = {
    connected: 'Connected to ROS 2',
    disconnected: 'Disconnected',
    error: 'Connection error',
  };

  return (
    <span className={`status-badge status-badge--${status}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      {labels[status]}
    </span>
  );
}

export default function App() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [messageCount, setMessageCount] = useState(0);
  const [temperature, setTemperature] = useState(null);
  const [sampleCount, setSampleCount] = useState(0);
  const [recorderState, setRecorderState] = useState('idle');
  const [recordedCount, setRecordedCount] = useState(0);
  const [lastAction, setLastAction] = useState('Waiting for your first command');

  const buttonTopicRef = useRef(null);
  const commandTopicRef = useRef(null);
  const messageCountRef = useRef(0);

  useEffect(() => {
    const ros = new ROSLIB.Ros({ url: ROSBRIDGE_URL });
    let reconnectTimer = null;
    let componentIsMounted = true;

    ros.on('connection', () => {
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      setConnectionStatus('connected');
    });
    ros.on('error', () => setConnectionStatus('error'));
    ros.on('close', () => {
      if (!componentIsMounted) return;
      setConnectionStatus('disconnected');
      reconnectTimer = window.setTimeout(() => ros.connect(ROSBRIDGE_URL), 2000);
    });

    const buttonTopic = new ROSLIB.Topic({
      ros,
      name: TOPICS.buttonPress,
      messageType: 'std_msgs/String',
    });
    const commandTopic = new ROSLIB.Topic({
      ros,
      name: TOPICS.recorderCommand,
      messageType: 'std_msgs/String',
    });
    const temperatureTopic = new ROSLIB.Topic({
      ros,
      name: TOPICS.temperature,
      messageType: 'std_msgs/Float32',
    });
    const recorderStatusTopic = new ROSLIB.Topic({
      ros,
      name: TOPICS.recorderStatus,
      messageType: 'std_msgs/String',
    });

    buttonTopicRef.current = buttonTopic;
    commandTopicRef.current = commandTopic;

    temperatureTopic.subscribe((message) => {
      setTemperature(Number(message.data));
      setSampleCount((current) => current + 1);
    });

    recorderStatusTopic.subscribe((message) => {
      const [nextState, count = '0'] = String(message.data).split(':');
      setRecorderState(nextState === 'recording' ? 'recording' : 'idle');
      setRecordedCount(Number.parseInt(count, 10) || 0);
    });

    return () => {
      componentIsMounted = false;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      temperatureTopic.unsubscribe();
      recorderStatusTopic.unsubscribe();
      buttonTopicRef.current = null;
      commandTopicRef.current = null;
      ros.close();
    };
  }, []);

  const publishButtonEvent = (label) => {
    if (connectionStatus !== 'connected' || !buttonTopicRef.current) return;

    const nextCount = messageCountRef.current + 1;
    messageCountRef.current = nextCount;
    setMessageCount(nextCount);
    buttonTopicRef.current.publish(
      new ROSLIB.Message({
        data: `${label} from React GUI. Count = ${nextCount}`,
      }),
    );
    setLastAction(label);
  };

  const sendRecorderCommand = (command, label) => {
    if (connectionStatus !== 'connected' || !commandTopicRef.current) return;

    publishButtonEvent(label);
    commandTopicRef.current.publish(new ROSLIB.Message({ data: command }));
  };

  const isConnected = connectionStatus === 'connected';
  const temperatureText =
    temperature === null || Number.isNaN(temperature)
      ? '--.--'
      : temperature.toFixed(2);

  return (
    <main className="app-shell">
      <section className="dashboard" aria-labelledby="page-title">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">Browser ↔ rosbridge ↔ ROS 2</p>
            <h1 id="page-title">ROS 2 Sensor Console</h1>
            <p className="subtitle">
              Publish commands, watch a live topic, and record readings to CSV.
            </p>
          </div>
          <ConnectionBadge status={connectionStatus} />
        </header>

        <div className="metrics-grid">
          <article className="metric-card metric-card--temperature">
            <span className="metric-label">Live temperature</span>
            <div className="temperature-value">
              {temperatureText}<span>°C</span>
            </div>
            <span className="metric-detail">
              {sampleCount.toLocaleString()} samples received
            </span>
          </article>

          <article className="metric-card">
            <span className="metric-label">CSV recorder</span>
            <strong className={`recorder-state recorder-state--${recorderState}`}>
              {recorderState === 'recording' ? 'Recording' : 'Idle'}
            </strong>
            <span className="metric-detail">
              {recordedCount.toLocaleString()} rows this session
            </span>
          </article>

          <article className="metric-card">
            <span className="metric-label">GUI events sent</span>
            <strong className="event-count">{messageCount}</strong>
            <span className="metric-detail">Topic: {TOPICS.buttonPress}</span>
          </article>
        </div>

        <section className="controls-card" aria-labelledby="controls-title">
          <div className="section-heading">
            <div>
              <h2 id="controls-title">Controls</h2>
              <p>Each control is also logged by the button listener node.</p>
            </div>
            <span className="last-action">Last: {lastAction}</span>
          </div>

          <div className="button-grid">
            <button
              className="action-button action-button--primary"
              onClick={() => publishButtonEvent('Test message sent')}
              disabled={!isConnected}
            >
              Send test message
            </button>
            <button
              className="action-button action-button--start"
              onClick={() => sendRecorderCommand('start', 'Recording started')}
              disabled={!isConnected || recorderState === 'recording'}
            >
              Start recording
            </button>
            <button
              className="action-button action-button--stop"
              onClick={() => sendRecorderCommand('stop', 'Recording stopped')}
              disabled={!isConnected || recorderState !== 'recording'}
            >
              Stop recording
            </button>
            <button
              className="action-button action-button--reset"
              onClick={() => sendRecorderCommand('reset', 'CSV reset')}
              disabled={!isConnected}
            >
              Reset CSV
            </button>
          </div>
        </section>

        <footer className="connection-note">
          <span>rosbridge</span>
          <code>{ROSBRIDGE_URL}</code>
          <span>sensor topic</span>
          <code>{TOPICS.temperature}</code>
        </footer>
      </section>
    </main>
  );
}
