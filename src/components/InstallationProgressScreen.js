import React, { useState, useEffect } from 'react';

const InstallationProgressScreen = ({ onNext, onBack }) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Preparing installation...');
  const [subProgress, setSubProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [installedComponents, setInstalledComponents] = useState([]);

  const steps = [
    'Preparing installation...',
    'Creating directories...',
    'Installing ML components...',
    'Setting up monitoring services...',
    'Configuring system integration...',
    'Finalizing installation...'
  ];

  const components = [
    { name: 'Core application files', threshold: 16.7, icon: '📱' },
    { name: 'System directories', threshold: 33.3, icon: '📁' },
    { name: 'ML monitoring engine', threshold: 50, icon: '🤖' },
    { name: 'Monitoring services', threshold: 66.7, icon: '⚙️' },
    { name: 'System integration', threshold: 83.3, icon: '🔗' },
    { name: 'Final configuration', threshold: 100, icon: '✨' }
  ];

  useEffect(() => {
    let currentIndex = 0;
    let subProgressInterval;
    
    const mainInterval = setInterval(async () => {
      if (currentIndex < steps.length) {
        setCurrentStep(steps[currentIndex]);
        setSubProgress(0);
        
        // Simulate sub-progress for each step
        subProgressInterval = setInterval(() => {
          setSubProgress(prev => {
            if (prev >= 100) {
              clearInterval(subProgressInterval);
              return 100;
            }
            return prev + Math.random() * 15;
          });
        }, 100);
        
        // Simulate backend installation process
        if (window.electronAPI) {
          await window.electronAPI.simulateInstallation(steps[currentIndex]);
        }
        
        const newProgress = ((currentIndex + 1) / steps.length) * 100;
        setProgress(newProgress);
        
        // Add completed components
        const completedComponent = components[currentIndex];
        if (completedComponent) {
          setInstalledComponents(prev => [...prev, completedComponent]);
        }
        
        currentIndex++;
      } else {
        clearInterval(mainInterval);
        clearInterval(subProgressInterval);
        setCurrentStep('Installation complete!');
        setSubProgress(100);
        setIsComplete(true);
      }
    }, 1000);

    return () => {
      clearInterval(mainInterval);
      if (subProgressInterval) clearInterval(subProgressInterval);
    };
  }, []);

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-blue-100 rounded-full mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl">📦</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Installing MyApp</h2>
        <p className="text-gray-600">Please wait while we install your application</p>
      </div>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{currentStep}</span>
          <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
        </div>
        
        {/* Main Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div
            className="bg-gradient-to-r from-blue-500 to-green-500 h-4 rounded-full transition-all duration-500 ease-out progress-bar"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        
        {/* Sub Progress Bar for Current Step */}
        {progress < 100 && (
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-blue-400 h-2 rounded-full transition-all duration-200 ease-out"
              style={{ width: `${Math.min(subProgress, 100)}%` }}
            ></div>
          </div>
        )}
      </div>

      <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600 mb-6">
        <p className="mb-3 font-medium">Installing components:</p>
        <div className="grid grid-cols-2 gap-3">
          {components.map((component, index) => {
            const isInstalled = progress >= component.threshold;
            const isCurrentlyInstalling = !isInstalled && index === Math.floor((progress / 100) * components.length);
            
            return (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-lg">{component.icon}</span>
                <span className={`flex-1 ${isInstalled ? 'text-green-600' : isCurrentlyInstalling ? 'text-blue-600' : 'text-gray-400'}`}>
                  {component.name}
                </span>
                <span className="text-sm">
                  {isInstalled ? '✅' : isCurrentlyInstalling ? '⏳' : '⏸️'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time Installation Log */}
      <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-xs mb-6 h-32 overflow-y-auto">
        <div className="space-y-1">
          <div>[INFO] Starting installation process...</div>
          {progress >= 16.7 && <div>[INFO] Creating installation directories...</div>}
          {progress >= 16.7 && <div>[INFO] Directory structure created successfully</div>}
          {progress >= 33.3 && <div>[INFO] Extracting ML component packages...</div>}
          {progress >= 33.3 && <div>[INFO] Installing TensorFlow dependencies...</div>}
          {progress >= 50 && <div>[INFO] Configuring monitoring services...</div>}
          {progress >= 50 && <div>[INFO] Setting up log aggregation pipeline...</div>}
          {progress >= 66.7 && <div>[INFO] Registering system hooks...</div>}
          {progress >= 66.7 && <div>[INFO] Configuring startup services...</div>}
          {progress >= 83.3 && <div>[INFO] Applying system integrations...</div>}
          {progress >= 83.3 && <div>[INFO] Setting up monitoring dashboards...</div>}
          {progress >= 100 && <div className="text-yellow-400">[SUCCESS] Installation completed successfully!</div>}
          {isComplete && (
            <div className="text-cyan-400">
              <div>[INFO] Ready to launch application...</div>
            </div>
          )}
        </div>
      </div>

      {/* Installation Statistics */}
      {progress >= 50 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg text-center">
            <div className="text-xl font-bold text-blue-600">{installedComponents.length}</div>
            <div className="text-xs text-blue-700">Components</div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg text-center">
            <div className="text-xl font-bold text-green-600">847MB</div>
            <div className="text-xs text-green-700">Installed</div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg text-center">
            <div className="text-xl font-bold text-purple-600">{Math.round((Date.now() % 10000) / 1000)}s</div>
            <div className="text-xs text-purple-700">Time Elapsed</div>
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={onBack}
          disabled={!isComplete}
          className={`px-6 py-2 transition-colors ${
            isComplete 
              ? 'text-gray-600 hover:text-gray-800 cursor-pointer' 
              : 'text-gray-400 cursor-not-allowed'
          }`}
        >
          ← Back
        </button>
        <button
          onClick={onNext}
          disabled={!isComplete}
          className={`px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
            isComplete
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isComplete ? 'Complete Installation →' : 'Installing...'}
        </button>
      </div>
    </div>
  );
};

export default InstallationProgressScreen;