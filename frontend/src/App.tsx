import { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import { NotificationProvider } from './context/NotificationContext';
import ErrorBoundary from './components/ErrorBoundary';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
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
import NotFoundPage from './pages/NotFoundPage';
import FamilyDashboardView from './components/FamilyDashboard';
import type { User } from './types';
import { getUsers } from './api';
import './App.css';
import './index.css';

function FamilyDashboardRoute() {
  const navigate = useNavigate();
  return <FamilyDashboardView onExit={() => navigate('/')} />;
}

function LoginRoute({ onLogin }: { onLogin: (user: User) => void }) {
  const navigate = useNavigate();
  return <Login onLogin={onLogin} onFamilyDashboard={() => navigate('/family-dashboard')} />;
}

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  const refreshUser = async () => {
    if (!currentUser) return;
    try {
      const res = await getUsers();
      const user = res.data.find((u: User) => u.id === currentUser.id);
      if (user) {
        setCurrentUser(user);
        localStorage.setItem('user', JSON.stringify(user)); // ensure local storage is sync
      }
    } catch (err) {
      console.error('Failed to refresh user', err);
    }
  };

  return (
    <ToastProvider>
      <ErrorBoundary>
        <BrowserRouter>
          {!currentUser ? (
            <Routes>
              <Route path="/family-dashboard" element={<FamilyDashboardRoute />} />
              <Route path="*" element={<LoginRoute onLogin={handleLogin} />} />
            </Routes>
          ) : (
            <NotificationProvider currentUser={currentUser}>
              <Routes>
                <Route path="/family-dashboard" element={<FamilyDashboardRoute />} />
                <Route
                  path="/"
                  element={<DashboardLayout currentUser={currentUser} onLogout={handleLogout} refreshUser={refreshUser} />}
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
                  <Route path="admin/analytics" element={<AnalyticsDashboard />} />
                  <Route path="settings" element={<SettingsPage />} />
                </Route>
                {/* Catch all - 404 page */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </NotificationProvider>
          )}
        </BrowserRouter>
      </ErrorBoundary>
    </ToastProvider>
  );
}

export default App;
