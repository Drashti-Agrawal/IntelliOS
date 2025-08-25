// src/pages/LiveMonitorScreen.js
import React from 'react';

const LiveMonitorScreen = () => {
  return (
    <div className="screen-container">
      <h2>Live Monitoring</h2>
      <p>Your system is being monitored in real-time...</p>
      <div className="monitor-box">
        <h4>CPU Usage: 45%</h4>
        <h4>Memory Usage: 60%</h4>
        <h4>Disk Usage: 70%</h4>
        <h4>Network Usage: 30%</h4>
      </div>
    </div>
  );
};

export default LiveMonitorScreen;
