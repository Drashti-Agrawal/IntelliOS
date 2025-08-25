import React, { useState } from 'react';

const PermissionsScreen = ({ onNext, onBack }) => {
  const [permissions, setPermissions] = useState({
    systemMonitoring: false,
    fileAccess: false,
    networkAccess: false,
    logSystemEvents: false
  });

  const handlePermissionChange = (key) => {
    setPermissions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const allPermissionsGranted = Object.values(permissions).every(Boolean);

  const permissionItems = [
    {
      key: 'systemMonitoring',
      icon: '🔍',
      label: 'Allow System Monitoring',
      desc: 'Monitor system performance, resource usage, and health metrics',
      required: true
    },
    {
      key: 'fileAccess',
      icon: '📁',
      label: 'Enable File Access',
      desc: 'Access log files, system directories, and configuration files',
      required: true
    },
    {
      key: 'networkAccess',
      icon: '🌐',
      label: 'Grant Network Access',
      desc: 'Connect to cloud services, download updates, and sync data',
      required: true
    },
    {
      key: 'logSystemEvents',
      icon: '📊',
      label: 'Log System Events',
      desc: 'Record and analyze system events for ML training and insights',
      required: true
    }
  ];

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-amber-100 rounded-full mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl">🔐</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Grant Permissions</h2>
        <p className="text-gray-600">Please grant the following permissions for optimal functionality</p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
        <div className="flex items-start space-x-3">
          <span className="text-yellow-600 text-lg">⚠️</span>
          <div>
            <h4 className="text-sm font-semibold text-yellow-800">Security Notice</h4>
            <p className="text-xs text-yellow-700 mt-1">
              These permissions are required for ML monitoring functionality. Your data remains private and secure.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4 mb-8">
        {permissionItems.map(({ key, icon, label, desc, required }) => (
          <div 
            key={key} 
            className={`flex items-start space-x-3 p-4 border rounded-lg transition-all duration-200 ${
              permissions[key] 
                ? 'border-green-200 bg-green-50' 
                : 'border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex-shrink-0 mt-1">
              <span className="text-xl">{icon}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={key}
                  checked={permissions[key]}
                  onChange={() => handlePermissionChange(key)}
                  className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
                <label htmlFor={key} className="text-sm font-medium text-gray-700 cursor-pointer">
                  {label}
                  {required && <span className="text-red-500 ml-1">*</span>}
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1 ml-7">{desc}</p>
            </div>
            {permissions[key] && (
              <div className="flex-shrink-0">
                <span className="text-green-500 text-sm">✓</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-blue-600">ℹ️</span>
          <h4 className="text-sm font-semibold text-blue-800">Why These Permissions?</h4>
        </div>
        <ul className="text-xs text-blue-700 space-y-1 ml-6">
          <li>• System monitoring enables real-time performance analytics</li>
          <li>• File access allows log processing and ML model training</li>
          <li>• Network access enables cloud sync and remote monitoring</li>
          <li>• Event logging provides data for intelligent system insights</li>
        </ul>
      </div>

      {/* Back and Next Buttons */}
      <div className="flex justify-between">
        <button
          onClick={onBack} // Goes back to WelcomeScreen
          className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={onNext} // Moves forward to InitialMonitoringScreen
          disabled={!allPermissionsGranted}
          className={`px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
            allPermissionsGranted
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {allPermissionsGranted ? 'Next →' : `Grant All Permissions (${Object.values(permissions).filter(Boolean).length}/4)`}
        </button>
      </div>
    </div>
  );
};

export default PermissionsScreen;
