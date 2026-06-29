// App.jsx
//
// This React component connects to ROS 2 through rosbridge using roslibjs,
// then publishes a std_msgs/String message to the /button_press topic every
// time the user clicks the button.
//
// Data flow reminder:
//   This component (roslibjs / WebSocket)
//     -> rosbridge_server (ws://localhost:9090)
//     -> ROS 2 topic /button_press
//     -> the Python button_listener node
//
// For students: ROSLIB is the browser library that speaks the rosbridge
// protocol. A "Topic" object is how we publish/subscribe from JavaScript.

import { useEffect, useRef, useState } from 'react';
import ROSLIB from 'roslib';

// The rosbridge URL comes from a Vite environment variable (set in
// docker-compose.yml). If it is missing, we fall back to localhost.
const ROSBRIDGE_URL =
  import.meta.env.VITE_ROSBRIDGE_URL || 'ws://localhost:9090';

export default function App() {
  // Connection status shown to the user: 'connected' | 'disconnected' | 'error'
  const [status, setStatus] = useState('disconnected');
  // How many times the button has been clicked.
  const [clickCount, setClickCount] = useState(0);

  // We keep the ROS connection and the Topic object in refs so they survive
  // re-renders without being re-created.
  const rosRef = useRef(null);
  const topicRef = useRef(null);

  useEffect(() => {
    // 1. Create the connection to rosbridge.
    const ros = new ROSLIB.Ros({ url: ROSBRIDGE_URL });
    rosRef.current = ros;

    // 2. React to connection lifecycle events.
    ros.on('connection', () => setStatus('connected'));
    ros.on('error', () => setStatus('error'));
    ros.on('close', () => setStatus('disconnected'));

    // 3. Describe the topic we want to publish on. This MUST match the topic
    //    name and message type that the Python node subscribes to.
    topicRef.current = new ROSLIB.Topic({
      ros,
      name: '/button_press',
      messageType: 'std_msgs/String',
    });

    // Clean up the connection when the component unmounts.
    return () => ros.close();
  }, []);

  // Called when the user clicks the button.
  const handleClick = () => {
    const nextCount = clickCount + 1;
    setClickCount(nextCount);

    // Build a std_msgs/String message. The single field is `data`.
    const message = new ROSLIB.Message({
      data: `Button clicked from React GUI. Count = ${nextCount}`,
    });

    // Publish it to /button_press. rosbridge forwards it into ROS 2.
    if (topicRef.current) {
      topicRef.current.publish(message);
    }
  };

  // --- Simple inline styles (no Tailwind, beginner-friendly) ----------------
  const styles = {
    page: {
      fontFamily: 'system-ui, Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#f4f6f8',
      color: '#1a1a1a',
      margin: 0,
    },
    card: {
      backgroundColor: '#ffffff',
      padding: '2.5rem',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
      textAlign: 'center',
      maxWidth: '420px',
      width: '90%',
    },
    title: { marginTop: 0, fontSize: '1.5rem' },
    status: {
      display: 'inline-block',
      padding: '0.4rem 0.9rem',
      borderRadius: '999px',
      fontWeight: 600,
      fontSize: '0.9rem',
      marginBottom: '1.5rem',
      color: '#ffffff',
      backgroundColor:
        status === 'connected'
          ? '#22a06b'
          : status === 'error'
          ? '#d9480f'
          : '#868e96',
    },
    button: {
      fontSize: '1rem',
      fontWeight: 600,
      padding: '0.9rem 1.5rem',
      border: 'none',
      borderRadius: '8px',
      backgroundColor: status === 'connected' ? '#1971c2' : '#adb5bd',
      color: '#ffffff',
      cursor: status === 'connected' ? 'pointer' : 'not-allowed',
      transition: 'background-color 0.2s',
    },
    count: { marginTop: '1.25rem', fontSize: '0.95rem', color: '#495057' },
    hint: { marginTop: '1.5rem', fontSize: '0.8rem', color: '#868e96' },
  };

  // Human-readable status text.
  const statusText =
    status === 'connected'
      ? 'Connected to ROS 2'
      : status === 'error'
      ? 'Connection error'
      : 'Disconnected';

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>ROS 2 + React Starter</h1>

        <div style={styles.status}>{statusText}</div>

        <div>
          <button
            style={styles.button}
            onClick={handleClick}
            disabled={status !== 'connected'}
          >
            Send Message to ROS
          </button>
        </div>

        <div style={styles.count}>Messages sent: {clickCount}</div>

        <div style={styles.hint}>
          Publishing <code>std_msgs/String</code> to <code>/button_press</code>
          <br />
          rosbridge: <code>{ROSBRIDGE_URL}</code>
        </div>
      </div>
    </div>
  );
}
