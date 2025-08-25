import React from 'react';
import '../styles/launch.css';
import { useNavigate } from 'react-router-dom';

const Launch = () => {
  const navigate = useNavigate();

  const handleLaunch = () => {
    navigate('/dashboard');
  };

  return (
    <div className="launch-container">
      <div className="launch-box">
        <h1>Launch IntelliOS Dashboard</h1>
        <button onClick={handleLaunch}>Launch Now</button>
      </div>
    </div>
  );
};

export default Launch;
