// src/pages/PermissionScreen.js
import React from 'react';
import PermissionCheckboxes from '../components/PermissionCheckboxes';
import { useNavigate } from 'react-router-dom';

const PermissionScreen = () => {
  const navigate = useNavigate();

  return (
    <div className="screen-container">
      <h2>Grant Permissions</h2>
      <PermissionCheckboxes />
      <button onClick={() => navigate('/monitoring')}>Continue</button>
    </div>
  );
};

export default PermissionScreen;
