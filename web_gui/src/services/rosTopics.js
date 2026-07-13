import ROSLIB from 'roslib';

export const ROS_TOPICS = {
  buttonPress: { name: '/button_press', messageType: 'std_msgs/String' },
  temperature: { name: '/sensor/temperature', messageType: 'std_msgs/Float32' },
  recorderCommand: { name: '/recorder/command', messageType: 'std_msgs/String' },
  recorderStatus: { name: '/recorder/status', messageType: 'std_msgs/String' },
  sdcCommand: { name: '/sdc/command', messageType: 'std_msgs/String' },
  sdcStatus: { name: '/sdc/status', messageType: 'std_msgs/String' },
  sdcSpeed: { name: '/sdc/speed', messageType: 'std_msgs/Float32' },
  sdcSteering: { name: '/sdc/steering', messageType: 'std_msgs/Float32' },
  sdcBattery: { name: '/sdc/battery', messageType: 'std_msgs/Float32' },
  sdcEvents: { name: '/sdc/events', messageType: 'std_msgs/String' },
};

export function getDefaultRosbridgeUrl() {
  if (typeof window !== 'undefined' && window.location) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}/rosbridge`;
  }
  return 'ws://localhost:9090';
}

export const ROSBRIDGE_URL =
  import.meta.env.VITE_ROSBRIDGE_URL || getDefaultRosbridgeUrl();

export function createRosTopics(ros) {
  return Object.fromEntries(
    Object.entries(ROS_TOPICS).map(([key, config]) => [
      key,
      new ROSLIB.Topic({ ros, ...config }),
    ]),
  );
}
