// src/components/MonitorBox.js
import React from 'react';

const MonitorBox = ({ status }) => {
  return (
    <div className="monitor-box">
      <p>{status}</p>
      <div className="progress-bar">
        <div className="progress" style={{ width: '50%' }}></div>
      </div>
    </div>
  );
};

export default MonitorBox;
