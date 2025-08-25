import React, { useState, useEffect } from 'react';

const InitialMonitoringScreen = ({ onNext, onBack, preferences, setPreferences }) => {
  const [installPath, setInstallPath] = useState('C:\\Program Files\\MyApp');
  const [showCloudSetup, setShowCloudSetup] = useState(false);

  const handlePreferenceChange = (key) => {
    setPreferences(prev => {
      const newPrefs = { ...prev, [key]: !prev[key] };
      
      // Show cloud setup notification when cloud sync is enabled
      if (key === 'cloudSync' && !prev[key]) {
        setShowCloudSetup(true);
        setTimeout(() => setShowCloudSetup(false), 3000);
      }
      
      return newPrefs;
    });
  };

  const selectDirectory = async () => {
    if (window.electronAPI) {
      const selectedPath = await window.electronAPI.selectDirectory();
      if (selectedPath) {
        setInstallPath(selectedPath);
        setPreferences(prev => ({ ...prev, installPath: selectedPath }));
      }
    }
  };

  useEffect(() => {
    setPreferences(prev => ({ ...prev, installPath }));
  }, [installPath, setPreferences]);

  const preferenceItems = [
    {
      key: 'cloudSync',
      icon: '☁️',
      label: 'Enable Cloud Sync',
      desc: 'Synchronize monitoring data across devices and backup to cloud',
      beta: false
    },
    {
      key: 'githubConnect',
      icon: '🐙',
      label: 'Connect GitHub',
      desc: 'Integrate with GitHub repositories for code monitoring and analytics',
      beta: true
    },
    {
      key: 'notifications',
      icon: '🔔',
      label: 'Enable Notifications',
      desc: 'Receive alerts for system events, anomalies, and important updates',
      beta: false
    },
    {
      key: 'autoBackup',
      icon: '💾',
      label: 'Enable Auto Backup',
      desc: 'Automatically backup monitoring data and ML models locally',
      beta: false
    }
  ];

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-green-100 rounded-full mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl">⚙️</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Initial Monitoring Setup</h2>
        <p className="text-gray-600">Configure installation preferences and monitoring options</p>
      </div>

      <div className="space-y-6 mb-8">
        {/* Installation Path Section */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            <span className="flex items-center space-x-2">
              <span>📁</span>
              <span>Installation Path</span>
            </span>
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={installPath}
              onChange={(e) => setInstallPath(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder="C:\Program Files\MyApp"
            />
            <button
              onClick={selectDirectory}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors text-sm font-medium"
            >
              Browse
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Recommended: Use default path for system-wide installation
          </p>
        </div>

        {/* Monitoring Preferences Section */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center space-x-2">
            <span>🔧</span>
            <span>Monitoring Preferences</span>
          </h3>
          <div className="space-y-3">
            {preferenceItems.map(({ key, icon, label, desc, beta }) => (
              <div 
                key={key} 
                className={`flex items-start space-x-3 p-4 border rounded-lg transition-all duration-200 ${
                  preferences[key] 
                    ? 'border-blue-200 bg-blue-50' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex-shrink-0 mt-1">
                  <span className="text-lg">{icon}</span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={key}
                      checked={preferences[key] || false}
                      onChange={() => handlePreferenceChange(key)}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <label htmlFor={key} className="text-sm font-medium text-gray-700 cursor-pointer flex items-center space-x-2">
                      <span>{label}</span>
                      {beta && (
                        <span className="bg-orange-100 text-orange-600 text-xs px-2 py-0.5 rounded-full font-normal">
                          Beta
                        </span>
                      )}
                    </label>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 ml-6">{desc}</p>
                </div>
                {preferences[key] && (
                  <div className="flex-shrink-0">
                    <span className="text-blue-500 text-sm">✓</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Cloud Setup Notification */}
        {showCloudSetup && (
          <div className="bg-blue-50 p-4 rounded-lg animate-slide-in border border-blue-200">
            <div className="flex items-start space-x-3">
              <span className="text-blue-600 text-lg">☁️</span>
              <div>
                <h4 className="text-sm font-medium text-blue-800">Cloud Setup Required</h4>
                <p className="text-xs text-blue-700 mt-1">
                  Cloud sync will be configured in the next step after installation. You'll need to sign in to your cloud account.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* GitHub Integration Notice */}
        {preferences.githubConnect && (
          <div className="bg-purple-50 p-4 rounded-lg animate-slide-in border border-purple-200">
            <div className="flex items-start space-x-3">
              <span className="text-purple-600 text-lg">🐙</span>
              <div>
                <h4 className="text-sm font-medium text-purple-800">GitHub Integration</h4>
                <p className="text-xs text-purple-700 mt-1">
                  You'll be prompted to authenticate with GitHub after installation to enable repository monitoring.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* System Requirements Check */}
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h4 className="text-sm font-medium text-green-800 mb-2">System Requirements ✓</h4>
          <div className="grid grid-cols-2 gap-2 text-xs text-green-700">
            <div>• Windows 10/11 ✓</div>
            <div>• 4GB RAM Available ✓</div>
            <div>• 2GB Disk Space ✓</div>
            <div>• Internet Connection ✓</div>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={onNext}
          className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Continue →
        </button>
      </div>
    </div>
  );
};

export default InitialMonitoringScreen;