import { useCallback, useEffect, useRef, useState } from 'react';
import ROSLIB from 'roslib';
import { createRosTopics, ROSBRIDGE_URL } from '../services/rosTopics.js';

const INITIAL_TELEMETRY = {
  temperature: null,
  speed: null,
  steering: null,
  battery: null,
};

function finiteNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

export function useRosBridge() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [telemetry, setTelemetry] = useState(INITIAL_TELEMETRY);
  const [vehicleStatus, setVehicleStatus] = useState('UNKNOWN');
  const [recorderState, setRecorderState] = useState('idle');
  const [recordedCount, setRecordedCount] = useState(0);
  const [sampleCount, setSampleCount] = useState(0);
  const [messageCount, setMessageCount] = useState(0);
  const [events, setEvents] = useState([]);
  const [lastAction, setLastAction] = useState('Waiting for your first command');

  const rosRef = useRef(null);
  const topicsRef = useRef(null);
  const messageCountRef = useRef(0);
  const eventIdRef = useRef(0);

  useEffect(() => {
    const ros = new ROSLIB.Ros();
    const topics = createRosTopics(ros);
    let componentIsMounted = true;
    let reconnectTimer = null;

    rosRef.current = ros;
    topicsRef.current = topics;

    const updateTelemetry = (key, value) => {
      const number = finiteNumber(value);
      if (number === null) return;
      setTelemetry((current) => ({ ...current, [key]: number }));
    };

    const onTemperature = (message) => {
      updateTelemetry('temperature', message.data);
      setSampleCount((current) => current + 1);
    };
    const onSpeed = (message) => updateTelemetry('speed', message.data);
    const onSteering = (message) => updateTelemetry('steering', message.data);
    const onBattery = (message) => updateTelemetry('battery', message.data);
    const onVehicleStatus = (message) => {
      const nextStatus = String(message.data || '').trim();
      if (nextStatus) setVehicleStatus(nextStatus);
    };
    const onRecorderStatus = (message) => {
      const [nextState, count = '0'] = String(message.data).split(':');
      setRecorderState(nextState === 'recording' ? 'recording' : 'idle');
      setRecordedCount(Number.parseInt(count, 10) || 0);
    };
    const onSdcEvent = (message) => {
      const text = String(message.data || '').trim();
      if (!text) return;

      eventIdRef.current += 1;
      const entry = {
        id: eventIdRef.current,
        timestamp: new Date().toLocaleTimeString([], { hour12: false }),
        message: text,
      };
      setEvents((current) => [entry, ...current].slice(0, 50));
    };

    topics.temperature.subscribe(onTemperature);
    topics.sdcSpeed.subscribe(onSpeed);
    topics.sdcSteering.subscribe(onSteering);
    topics.sdcBattery.subscribe(onBattery);
    topics.sdcStatus.subscribe(onVehicleStatus);
    topics.recorderStatus.subscribe(onRecorderStatus);
    topics.sdcEvents.subscribe(onSdcEvent);

    const onConnection = () => {
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      reconnectTimer = null;
      setConnectionStatus('connected');
    };
    const onError = () => {
      if (componentIsMounted) setConnectionStatus('error');
    };
    const onClose = () => {
      if (!componentIsMounted) return;
      setConnectionStatus('disconnected');
      if (!reconnectTimer) {
        reconnectTimer = window.setTimeout(() => {
          reconnectTimer = null;
          if (componentIsMounted) ros.connect(ROSBRIDGE_URL);
        }, 2000);
      }
    };

    ros.on('connection', onConnection);
    ros.on('error', onError);
    ros.on('close', onClose);
    ros.connect(ROSBRIDGE_URL);

    return () => {
      componentIsMounted = false;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);

      topics.temperature.unsubscribe(onTemperature);
      topics.sdcSpeed.unsubscribe(onSpeed);
      topics.sdcSteering.unsubscribe(onSteering);
      topics.sdcBattery.unsubscribe(onBattery);
      topics.sdcStatus.unsubscribe(onVehicleStatus);
      topics.recorderStatus.unsubscribe(onRecorderStatus);
      topics.sdcEvents.unsubscribe(onSdcEvent);

      for (const key of ['buttonPress', 'recorderCommand', 'sdcCommand']) {
        if (topics[key].isAdvertised) topics[key].unadvertise();
      }

      ros.off('connection', onConnection);
      ros.off('error', onError);
      ros.off('close', onClose);
      if (ros.isConnected) ros.close();
      rosRef.current = null;
      topicsRef.current = null;
    };
  }, []);

  const publishString = useCallback((topicKey, data) => {
    const ros = rosRef.current;
    const topic = topicsRef.current?.[topicKey];
    if (!ros?.isConnected || !topic) return false;

    topic.publish(new ROSLIB.Message({ data }));
    return true;
  }, []);

  const publishButtonEvent = useCallback(
    (label) => {
      const nextCount = messageCountRef.current + 1;
      const sent = publishString(
        'buttonPress',
        `${label} from React GUI. Count = ${nextCount}`,
      );
      if (!sent) return false;

      messageCountRef.current = nextCount;
      setMessageCount(nextCount);
      setLastAction(label);
      return true;
    },
    [publishString],
  );

  const sendTestMessage = useCallback(
    () => publishButtonEvent('Test message sent'),
    [publishButtonEvent],
  );

  const sendRecorderCommand = useCallback(
    (command, label) => {
      const sent = publishString('recorderCommand', command);
      if (!sent) return false;
      publishButtonEvent(label);
      setLastAction(label);
      return true;
    },
    [publishButtonEvent, publishString],
  );

  const sendVehicleCommand = useCallback(
    (command) => {
      const sent = publishString('sdcCommand', command);
      if (sent) setLastAction(command.replaceAll('_', ' '));
      return sent;
    },
    [publishString],
  );

  const clearEvents = useCallback(() => setEvents([]), []);

  return {
    connectionStatus,
    telemetry,
    vehicleStatus,
    recorderState,
    recordedCount,
    sampleCount,
    messageCount,
    events,
    lastAction,
    sendTestMessage,
    sendRecorderCommand,
    sendVehicleCommand,
    clearEvents,
  };
}
