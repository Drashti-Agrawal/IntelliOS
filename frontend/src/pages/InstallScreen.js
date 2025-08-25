// src/pages/InstallScreen.js
import React from 'react';
import { useNavigate } from 'react-router-dom';

const InstallScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="screen-container">
      <h1>Welcome to IntelliOS</h1>
      <p>Click below to start the installation process</p>
      <button onClick={() => navigate('/permissions')}>Install</button>
    </div>
  );
};

export default InstallScreen;
