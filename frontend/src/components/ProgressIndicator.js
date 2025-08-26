import React from 'react';

const ProgressIndicator = ({ steps, currentStep }) => {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
          >
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                index <= currentStep
                  ? 'bg-blue-600 text-white shadow-lg transform scale-110'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {index < currentStep ? (
                <span className="text-xs">✓</span>
              ) : (
                <span>{index + 1}</span>
              )}
            </div>
            {index < steps.length - 1 && (
              <div
                className={`flex-1 h-1 mx-4 transition-all duration-500 ${
                  index < currentStep 
                    ? 'bg-blue-600' 
                    : index === currentStep 
                    ? 'bg-gradient-to-r from-blue-600 to-gray-200' 
                    : 'bg-gray-200'
                }`}
              ></div>
            )}
          </div>
        ))}
      </div>
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-700">
          Step {currentStep + 1} of {steps.length}: {steps[currentStep]}
        </h3>
        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;