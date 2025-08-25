import React, { useState, useEffect } from 'react';

const LiveMonitoringScreen = ({ onNext, onBack }) => {
  const [monitoringProgress, setMonitoringProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('Initializing ML Model...');
  const [completedTasks, setCompletedTasks] = useState([]);
  const [isProcessing, setIsProcessing] = useState(true);

  const tasks = [
    { 
      name: 'Fetching recent logs', 
      progress: 15,
      detail: 'Scanning system logs and event data...',
      icon: '📄'
    },
    { 
      name: 'Preprocessing log data', 
      progress: 30,
      detail: 'Cleaning and structuring log entries...',
      icon: '🔄'
    },
    { 
      name: 'Loading ML model', 
      progress: 50,
      detail: 'Initializing TensorFlow and neural networks...',
      icon: '🤖'
    },
    { 
      name: 'Fine tuning for personalization', 
      progress: 75,
      detail: 'Adapting model to your system patterns...',
      icon: '⚡'
    },
    { 
      name: 'Generating personalized ML model', 
      progress: 90,
      detail: 'Creating custom monitoring profile...',
      icon: '🧠'
    },
    { 
      name: 'Setting up monitoring pipeline', 
      progress: 100,
      detail: 'Configuring real-time data processing...',
      icon: '🔧'
    }
  ];

  const backgroundProcesses = [
    { name: 'ML Model Training', status: 'active', color: 'green' },
    { name: 'Local DNA Generation', status: 'active', color: 'blue' },
    { name: 'Scheduled Job Setup', status: 'active', color: 'purple' },
    { name: 'Cloud DNA Pipeline', status: 'pending', color: 'orange' },
    { name: 'Cross-platform Sync', status: 'pending', color: 'cyan' },
    { name: 'Storage Configuration', status: 'pending', color: 'pink' }
  ];

  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < tasks.length) {
        const task = tasks[currentIndex];
        setCurrentTask(task.name);
        setMonitoringProgress(task.progress);
        
        // Add completed task to the list
        if (currentIndex > 0) {
          setCompletedTasks(prev => [...prev, tasks[currentIndex - 1]]);
        }
        
        currentIndex++;
      } else {
        clearInterval(interval);
        setIsProcessing(false);
        setCurrentTask('Live monitoring setup complete!');
        setCompletedTasks(prev => [...prev, tasks[tasks.length - 1]]);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, []);

  const getProcessStatus = (index) => {
    if (monitoringProgress >= 25 && index < 3) return 'active';
    if (monitoringProgress >= 75 && index >= 3) return 'active';
    return 'pending';
  };

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-purple-100 rounded-full mx-auto mb-4 flex items-center justify-center">
          <span className="text-2xl">🤖</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Live Monitoring Setup</h2>
        <p className="text-gray-600">Setting up ML model and monitoring pipeline</p>
      </div>

      {/* Main Progress Section */}
      <div className="bg-gray-50 p-6 rounded-lg mb-6">
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 flex items-center space-x-2">
              <span>{tasks.find(t => t.name === currentTask)?.icon || '⚙️'}</span>
              <span>{currentTask}</span>
            </span>
            <span className="text-sm text-gray-500">{monitoringProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${monitoringProgress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500">
            {tasks.find(t => t.name === currentTask)?.detail || 'Processing...'}
          </p>
        </div>

        {/* Completed Tasks */}
        {completedTasks.length > 0 && (
          <div className="bg-white p-4 rounded-lg mb-4">
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Completed Tasks:</h4>
            <div className="space-y-2">
              {completedTasks.map((task, index) => (
                <div key={index} className="flex items-center space-x-3 text-xs">
                  <span className="text-green-500">✅</span>
                  <span className="text-lg">{task.icon}</span>
                  <span className="text-gray-700">{task.name}</span>
                  <span className="text-gray-400 ml-auto">{task.progress}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Background Processing */}
        <div className="bg-white p-4 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Background Processing:</h4>
          <div className="grid grid-cols-2 gap-3 text-xs">
            {backgroundProcesses.map((process, index) => {
              const status = getProcessStatus(index);
              const colorMap = {
                green: 'bg-green-500',
                blue: 'bg-blue-500',
                purple: 'bg-purple-500',
                orange: 'bg-orange-500',
                cyan: 'bg-cyan-500',
                pink: 'bg-pink-500'
              };
              
              return (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className={`w-2 h-2 rounded-full ${
                      status === 'active' 
                        ? `${colorMap[process.color]} animate-pulse` 
                        : 'bg-gray-300'
                    }`}
                  ></div>
                  <span className={status === 'active' ? 'text-gray-700' : 'text-gray-400'}>
                    {process.name}
                  </span>
                  {status === 'active' && (
                    <span className="text-green-500 text-xs">●</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Real-time System Status */}
      <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-xs mb-6 h-32 overflow-y-auto">
        <div className="space-y-1">
          <div>[INFO] Initializing ML monitoring system...</div>
          {monitoringProgress >= 15 && <div>[INFO] Log fetcher started - Found 2,847 entries</div>}
          {monitoringProgress >= 15 && <div>[INFO] Connecting to system event stream...</div>}
          {monitoringProgress >= 30 && <div>[INFO] Preprocessing pipeline active</div>}
          {monitoringProgress >= 30 && <div>[INFO] Data normalization complete</div>}
          {monitoringProgress >= 50 && <div>[INFO] Loading TensorFlow model v2.1.3...</div>}
          {monitoringProgress >= 50 && <div>[INFO] Neural network initialized (784->128->64->32)</div>}
          {monitoringProgress >= 75 && <div>[INFO] Personalization layer active</div>}
          {monitoringProgress >= 75 && <div>[INFO] Learning system patterns...</div>}
          {monitoringProgress >= 90 && <div>[INFO] Generating custom DNA signatures...</div>}
          {monitoringProgress >= 90 && <div>[INFO] Local DNA: 127 patterns identified</div>}
          {monitoringProgress >= 100 && <div className="text-yellow-400">[SUCCESS] ML monitoring system online!</div>}
          {monitoringProgress >= 100 && <div className="text-cyan-400">[INFO] Ready for real-time analysis</div>}
        </div>
      </div>

      {/* Performance Metrics */}
      {monitoringProgress >= 75 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">98.7%</div>
            <div className="text-xs text-blue-700">Accuracy</div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">127</div>
            <div className="text-xs text-green-700">Patterns</div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">2.3s</div>
            <div className="text-xs text-purple-700">Response Time</div>
          </div>
        </div>
      )}

      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          disabled={isProcessing}
        >
          ← Back
        </button>
                <button
          onClick={onNext}
          disabled={monitoringProgress < 100}
          className={`px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
            monitoringProgress >= 100
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {monitoringProgress >= 100 ? 'Next →' : 'Processing...'}
        </button>
      </div>
    </div>
  );
};

export default LiveMonitoringScreen;
