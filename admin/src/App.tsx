import { useState, useEffect } from 'react';
import './App.css';
import Login from './auth/login';
import AdminLayout, { type AdminPage } from './layouts/AdminLayout';
import Dashboard from './pages/dashboard';
import PondManagement from './pages/pondManagement';
import UserManagement from './pages/userManagement';
import DataRecords from './pages/dataRecord';
import { AuthService } from './services/authService';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState<AdminPage>('dashboard');

  // Check authentication on component mount
  useEffect(() => {
    if (AuthService.isAuthenticated()) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    AuthService.logout();
    setIsLoggedIn(false);
    setCurrentPage('dashboard');
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <AdminLayout currentPage={currentPage} onNavigate={setCurrentPage} onLogout={handleLogout}>
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'ponds' && <PondManagement />}
      {currentPage === 'users' && <UserManagement />}
      {currentPage === 'data' && <DataRecords />}
    </AdminLayout>
  );
}

export default App;
