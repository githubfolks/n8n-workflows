import React, { useState } from 'react';
import { login } from '../services/api';

function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(username, password);
      onLoginSuccess(data.access_token);
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="view-login" className="view active">
      <div className="dashboard-header" style={{ justifyContent: 'center' }}>
        <h2>Login to Story Forge</h2>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="login-username">Username:</label>
          <input 
            type="text" 
            id="login-username" 
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="input-group">
          <label htmlFor="login-password">Password:</label>
          <input 
            type="password" 
            id="login-password" 
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && <div className="error-msg" style={{ textAlign: 'center', marginBottom: '1rem' }}>{error}</div>}
        <button type="submit" className="primary-btn" disabled={loading}>
          <span>{loading ? 'Logging in...' : 'Login'}</span>
          <div className="btn-glow"></div>
        </button>
      </form>
    </section>
  );
}

export default Login;
