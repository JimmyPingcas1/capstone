import { useState } from 'react';
import '../styles/login.css';
import { AuthService } from '../services/authService';

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({
    username: '',
    password: ''
  });

  const validateUsername = (value: string): string => {
    if (!value.trim()) {
      return 'Username is required';
    }
    if (value.length < 3) {
      return 'Username must be at least 3 characters';
    }
    if (value.length > 50) {
      return 'Username must not exceed 50 characters';
    }
    return '';
  };

  const validatePassword = (value: string): string => {
    if (!value) {
      return 'Password is required';
    }
    if (value.length < 6) {
      return 'Password must be at least 6 characters';
    }
    if (value.length > 100) {
      return 'Password must not exceed 100 characters';
    }
    return '';
  };

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsername(value);
    setValidationErrors(prev => ({
      ...prev,
      username: validateUsername(value)
    }));
    setError('');
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    setValidationErrors(prev => ({
      ...prev,
      password: validatePassword(value)
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const usernameError = validateUsername(username);
    const passwordError = validatePassword(password);
    
    setValidationErrors({
      username: usernameError,
      password: passwordError
    });

    // If there are validation errors, don't submit
    if (usernameError || passwordError) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Call the API with username as email
      await AuthService.login({
        email: username,
        password: password
      });
      
      // If successful, trigger login
      onLogin();
    } catch (err: any) {
      setError(err.message || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <div className="icon-circle">
            <img src="/fishpond-logo.png" alt="Fishpond logo" className="login-logo-image" />
          </div>
          <h1 className="login-title">Fishpond Admin</h1>
          <p className="login-subtitle">Water Quality Monitoring System</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message" style={{
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              color: '#c00',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '16px',
              fontSize: '14px'
            }}>
              {error}
            </div>
          )}

          <div className="input-group">
            <label className="input-label">Admin Username</label>
            <input
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Enter admin username"
              className={`input-field ${validationErrors.username ? 'input-error' : ''}`}
              disabled={isLoading}
              autoComplete="username"
            />
            {validationErrors.username && (
              <span className="validation-error" style={{
                color: '#c00',
                fontSize: '12px',
                marginTop: '4px',
                display: 'block'
              }}>
                {validationErrors.username}
              </span>
            )}
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <input
              type="password"
              value={password}
              onChange={handlePasswordChange}
              placeholder="Enter password"
              className={`input-field ${validationErrors.password ? 'input-error' : ''}`}
              disabled={isLoading}
              autoComplete="current-password"
            />
            {validationErrors.password && (
              <span className="validation-error" style={{
                color: '#c00',
                fontSize: '12px',
                marginTop: '4px',
                display: 'block'
              }}>
                {validationErrors.password}
              </span>
            )}
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
            style={{
              opacity: isLoading ? 0.7 : 1,
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Logging in...' : 'Enter to Dashboard'}
          </button>
        </form>

        <p className="login-footer">© 2026 Fishpond Monitoring System</p>
      </div>
    </div>
  );
}