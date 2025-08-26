import React from 'react';

const WelcomeScreen = ({ onNext }) => {
  return (
    <div className="text-center animate-fade-in">
      <div className="mb-8">
        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto mb-6 flex items-center justify-center">
          <span className="text-3xl font-bold text-white">IO</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-800 mb-2">IntelliOS</h1>
        <p className="text-lg text-gray-600 mb-2">Version 1.0.0</p>
        <p className="text-sm text-gray-500">Advanced ML-powered system monitoring and analytics</p>
      </div>
      
      <div className="bg-blue-50 p-6 rounded-lg mb-8">
        <h3 className="text-lg font-semibold text-blue-800 mb-3">What's New:</h3>
        <ul className="text-sm text-blue-700 space-y-2 text-left">
          <li>• Real-time ML-based system monitoring</li>
          <li>• Cloud synchronization and backup</li>
          <li>• Advanced log preprocessing and analytics</li>
          <li>• Personalized monitoring profiles</li>
          <li>• GitHub integration for code monitoring</li>
          <li>• Automated DNA generation and analysis</li>
        </ul>
      </div>
      
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg mb-8">
        <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span>System Ready</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <span>ML Engine Ready</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
            <span>Cloud Connected</span>
          </div>
        </div>
      </div>
      
      {/* Next Button */}
      <button
        onClick={onNext} // Moves to PermissionsScreen in the wizard
        className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
      >
        Next → 
      </button>
      
      <p className="text-xs text-gray-400 mt-4">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </p>
    </div>
  );
};

export default WelcomeScreen;
