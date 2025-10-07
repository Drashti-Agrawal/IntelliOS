import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './components/LoginPage';

import Dashboard from './components/Dashboard';
import WelcomeScreen from './components/WelcomeScreen';
import PermissionsScreen from './components/PermissionsScreen';
import InitialMonitoringScreen from './components/InitialMonitoringScreen';
import LiveMonitoringScreen from './components/LiveMonitoringScreen';
import InstallationProgressScreen from './components/InstallationProgressScreen';
import CompletionScreen from './components/CompletionScreen';
import ProgressIndicator from './components/ProgressIndicator';

import './index.css';
// import './styles/app.css';

const InstallerWizard = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [preferences, setPreferences] = useState({
    installPath: 'C:\\Program Files\\MyApp',
    cloudSync: false,
    githubConnect: false,
    notifications: true,
    autoBackup: false
  });

  const steps = [
    'Welcome',
    'Permissions',
    'Initial Monitoring',
    'Live Monitoring',
    'Installation',
    'Complete'
  ];

  const handleNext = () => setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  const handleBack = () => setCurrentStep(prev => Math.max(prev - 1, 0));

  const handleLaunch = async () => {
    if (window.electronAPI) {
      await window.electronAPI.launchApp(preferences);
    } else {
      console.log('Launching app with preferences:', preferences);
      alert('App would launch here in Electron environment');
    }
  };

  const renderStep = () => {
    const stepProps = {
      onNext: handleNext,
      onBack: handleBack,
      preferences,
      setPreferences,
      onLaunch: handleLaunch
    };

    const stepComponents = [
      <WelcomeScreen {...stepProps} />,
      <PermissionsScreen {...stepProps} />,
      <InitialMonitoringScreen {...stepProps} />,
      <LiveMonitoringScreen {...stepProps} />,
      <InstallationProgressScreen {...stepProps} />,
      <CompletionScreen {...stepProps} />
    ];

    return stepComponents[currentStep];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <ProgressIndicator steps={steps} currentStep={currentStep} />
        <div className="bg-white rounded-xl shadow-lg p-8 step-transition">
          {renderStep()}
        </div>
        <div className="text-center mt-6 text-sm text-gray-500">
          <p>MyApp ML Monitoring Installer v1.0.0</p>
          <p>© 2024 MyCompany. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Route-based pages */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Step-based installer wizard */}
        <Route path="/installer" element={<InstallerWizard />} />

        {/* Default route redirects to installer */}
        <Route path="*" element={<InstallerWizard />} />
      </Routes>
    </Router>
  );
};

export default App;
