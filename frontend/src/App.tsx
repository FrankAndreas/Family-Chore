import { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import { NotificationProvider } from './context/NotificationContext';
import ErrorBoundary from './components/ErrorBoundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import DashboardLayout from './layouts/DashboardLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import UserManagement from './pages/admin/UserManagement';
import TaskManagement from './pages/admin/TaskManagement';
import RoleManagement from './pages/admin/RoleManagement';
import UserDashboard from './pages/user/UserDashboard';
import RewardHub from './pages/user/RewardHub';
import AnalyticsDashboard from './pages/admin/AnalyticsDashboard';
import SettingsPage from './pages/SettingsPage';
import type { User } from './types';
import './App.css';
import './index.css';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  // If not logged in, show login page
  if (!currentUser) {
    return (
      <ToastProvider>
        <Login onLogin={handleLogin} />
      </ToastProvider>
    );
  }

  // If logged in, show dashboard with routes
  return (
    <ToastProvider>
      <NotificationProvider currentUser={currentUser}>
        <ErrorBoundary>
          <BrowserRouter>
            <Routes>
              <Route
                path="/"
                element={<DashboardLayout currentUser={currentUser} onLogout={handleLogout} />}
              >
                {/* Redirect root to appropriate dashboard */}
                <Route
                  index
                  element={<Navigate to={currentUser.role.name === 'Admin' ? '/admin' : '/dashboard'} replace />}
                />

                {/* Admin Routes */}
                <Route path="admin" element={<AdminDashboard />} />
                <Route path="admin/users" element={<UserManagement />} />
                <Route path="admin/tasks" element={<TaskManagement />} />
                <Route path="admin/roles" element={<RoleManagement />} />

                {/* User Routes */}
                <Route path="dashboard" element={<UserDashboard />} />
                <Route path="rewards" element={<RewardHub />} />
                <Route path="analytics" element={<AnalyticsDashboard />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>

              {/* Catch all - redirect to home */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </ErrorBoundary>
      </NotificationProvider>
    </ToastProvider>
  );
}

export default App;
