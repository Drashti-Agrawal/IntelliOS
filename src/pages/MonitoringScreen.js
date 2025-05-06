// src/pages/MonitoringScreen.js
import React from 'react';
import MonitorBox from '../components/MonitorBox';
import { useNavigate } from 'react-router-dom';

const MonitoringScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="screen-container">
      <h2>Initial Monitoring in Progress...</h2>
      <MonitorBox status="Collecting logs..." />
      <button onClick={() => navigate('/customize')}>Next</button>
    </div>
  );
};

export default MonitoringScreen;
