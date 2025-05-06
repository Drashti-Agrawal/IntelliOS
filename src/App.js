import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Launch from './pages/Launch';
import Dashboard from './pages/Dashboard';
import InstallScreen from './pages/InstallScreen';
import PermissionScreen from './pages/PermissionScreen';
import MonitoringScreen from './pages/MonitoringScreen';
import CustomizeScreen from './pages/CustomizeScreen';
import LiveMonitorScreen from './pages/LiveMonitorScreen';
import './styles/app.css';
function App() {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<InstallScreen />} />
        <Route path="/permissions" element={<PermissionScreen />} />
        <Route path="/monitoring" element={<MonitoringScreen />} />
        <Route path="/customize" element={<CustomizeScreen />} />
        <Route path="/live-monitoring" element={<LiveMonitorScreen />} />
        <Route path="/login" element={<Login />} />
        <Route path="/launch" element={<Launch />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
