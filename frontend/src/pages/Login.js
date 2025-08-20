import React, { useState } from 'react';
import '../styles/login.css';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [pin, setPin] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    if (pin === '1234') {  // You can replace this with any validation or backend call
      navigate('/launch');
    } else {
      alert('Invalid PIN');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Enter PIN to Access IntelliOS</h2>
        <input
          type="password"
          placeholder="Enter PIN"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
        />
        <button onClick={handleLogin}>Unlock</button>
      </div>
    </div>
  );
};

export default Login;
