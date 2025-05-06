import React from 'react';
import { useNavigate } from 'react-router-dom';

const CustomizeScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="screen-container">
      <h2>Customize Preferences</h2>
      <p>Adjust settings based on your needs. Cloud sync and GitHub optional.</p>
      <label>
        <input type="checkbox" /> Enable Cloud Sync
      </label>
      <label>
        <input type="checkbox" /> Connect GitHub
      </label>
      <button onClick={() => navigate('/live-monitor')}>Proceed</button>
    </div>
  );
};

export default CustomizeScreen;