import { useState } from 'react';
import { Eye, EyeOff, Github, Cloud, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
//import { User, Lock } from "lucide-react";

export default function LoginPage() {
  const [authMode, setAuthMode] = useState('cross-desktop'); // 'cross-desktop' or 'same-device'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    otpCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showMFA, setShowMFA] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [authStatus, setAuthStatus] = useState(null); // 'success', 'error', null

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = () => {
    const newErrors = {};

    if (authMode === 'same-device') {
      if (!formData.email.trim()) {
        newErrors.email = 'Email/Username is required';
      } else if (formData.email.includes('@') && !validateEmail(formData.email)) {
        newErrors.email = 'Please enter a valid email address';
      }

      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 6) {
        newErrors.password = 'Password must be at least 6 characters';
      }

      if (showMFA && !formData.otpCode) {
        newErrors.otpCode = 'OTP code is required';
      } else if (showMFA && formData.otpCode.length !== 6) {
        newErrors.otpCode = 'OTP code must be 6 digits';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Electron navigation after successful authentication
  const navigateToDashboard = () => {
    if (window.electronAPI && window.electronAPI.navigateToDashboard) {
      window.electronAPI.navigateToDashboard();
    } else {
      console.warn('Electron API not found. Implement navigateToDashboard in preload.js');
    }
  };

  const simulateAuth = async () => {
    setIsLoading(true);
    setAuthStatus(null);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Simulate random success/failure (80% success rate)
    const isSuccess = Math.random() > 0.2;

    if (isSuccess) {
      setAuthStatus('success');
      // Redirect to Dashboard in Electron
      setTimeout(() => {
        navigateToDashboard();
      }, 500);
    } else {
      setAuthStatus('error');
    }

    setIsLoading(false);
  };

  const handleOAuthLogin = async () => {
    await simulateAuth();
  };

  const handleFormLogin = async () => {
    if (!validateForm()) {
      return;
    }

    await simulateAuth();
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const resetForm = () => {
    setFormData({ email: '', password: '', otpCode: '' });
    setErrors({});
    setAuthStatus(null);
    setShowMFA(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome Back
            </h1>
            <p className="text-gray-600">
              Choose your authentication method
            </p>
          </div>

          {/* Auth Mode Selection */}
          <div className="mb-8">
            <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => {
                  setAuthMode('cross-desktop');
                  resetForm();
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                  authMode === 'cross-desktop'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Cross-Desktop Sync
              </button>
              <button
                onClick={() => {
                  setAuthMode('same-device');
                  resetForm();
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                  authMode === 'same-device'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Same-Device Restore
              </button>
            </div>
          </div>

          {/* Status Messages */}
          {authStatus === 'success' && (
            <div className="mb-6 flex items-center justify-center space-x-2 text-green-600 bg-green-50 rounded-lg p-3">
              <CheckCircle className="h-5 w-5" />
              <span className="font-medium">Authentication successful!</span>
            </div>
          )}
          {authStatus === 'error' && (
            <div className="mb-6 flex items-center justify-center space-x-2 text-red-600 bg-red-50 rounded-lg p-3">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Authentication failed. Please try again.</span>
            </div>
          )}

          {/* Cross-Desktop OAuth Login */}
          {authMode === 'cross-desktop' && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <p className="text-sm text-gray-600">
                  Sync your workspace across multiple devices
                </p>
              </div>

              <button
                onClick={handleOAuthLogin}
                disabled={isLoading}
                className="w-full flex items-center justify-center space-x-3 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 text-white py-3 px-4 rounded-lg font-semibold transition-colors duration-200"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Github className="h-5 w-5" />
                )}
                <span>{isLoading ? 'Connecting...' : 'Login with GitHub'}</span>
              </button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">or</span>
                </div>
              </div>

              <button
                onClick={handleOAuthLogin}
                disabled={isLoading}
                className="w-full flex items-center justify-center space-x-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-lg font-semibold transition-colors duration-200"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Cloud className="h-5 w-5" />
                )}
                <span>{isLoading ? 'Connecting...' : 'Login with Cloud'}</span>
              </button>
            </div>
          )}

          {/* Same-Device Form Login */}
          {authMode === 'same-device' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <p className="text-sm text-gray-600">
                  Restore your workspace on this device
                </p>
              </div>

              {/* Email/Username Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email or Username
                </label>
                <input
                  type="text"
                  id="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 ${
                    errors.email ? 'border-red-500 bg-red-50' : 'border-gray-300'
                  }`}
                  placeholder="Enter your email or username"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 pr-10 ${
                      errors.password ? 'border-red-500 bg-red-50' : 'border-gray-300'
                    }`}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password}</p>
                )}
              </div>

              {/* MFA Toggle */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="mfa-toggle"
                  checked={showMFA}
                  onChange={(e) => setShowMFA(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="mfa-toggle" className="ml-2 block text-sm text-gray-700">
                  I have Multi-Factor Authentication enabled
                </label>
              </div>

              {/* MFA Code Field */}
              {showMFA && (
                <div>
                  <label htmlFor="otpCode" className="block text-sm font-medium text-gray-700 mb-2">
                    6-Digit OTP Code
                  </label>
                  <input
                    type="text"
                    id="otpCode"
                    value={formData.otpCode}
                    onChange={(e) => handleInputChange('otpCode', e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 text-center font-mono text-lg tracking-widest ${
                      errors.otpCode ? 'border-red-500 bg-red-50' : 'border-gray-300'
                    }`}
                    placeholder="000000"
                    maxLength="6"
                  />
                  {errors.otpCode && (
                    <p className="mt-1 text-sm text-red-600">{errors.otpCode}</p>
                  )}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="button"
                onClick={handleFormLogin}
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <span>Login</span>
                )}
              </button>
            </div>
          )}

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500">
              Need help?{' '}
              <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                Contact Support
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
