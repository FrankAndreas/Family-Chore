import { useState, useEffect, lazy, Suspense } from 'react';
import { ToastProvider } from './context/ToastContext';
import { NotificationProvider } from './context/NotificationContext';
import { UserContext } from './context/UserContext';
import ErrorBoundary from './components/ErrorBoundary';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import DashboardLayout from './layouts/DashboardLayout';
import FamilyDashboardView from './components/FamilyDashboard';
import NotFoundPage from './pages/NotFoundPage';
import { SkeletonLoader } from './components/SkeletonLoader';
import type { User } from './types';
import { getUsers, registerForceLogout } from './api';
import './App.css';
import './index.css';

// Route-level code-splitting: each page loads as a separate JS chunk on first navigation.
// Login, DashboardLayout, FamilyDashboardView, and ErrorBoundary are kept eager
// because they render immediately and are tiny.
const AdminDashboard   = lazy(() => import('./pages/admin/AdminDashboard'));
const UserManagement   = lazy(() => import('./pages/admin/UserManagement'));
const TaskManagement   = lazy(() => import('./pages/admin/TaskManagement'));
const RoleManagement   = lazy(() => import('./pages/admin/RoleManagement'));
const UserDashboard    = lazy(() => import('./pages/user/UserDashboard'));
const RewardHub        = lazy(() => import('./pages/user/RewardHub'));
const AnalyticsDashboard = lazy(() => import('./pages/admin/AnalyticsDashboard'));
const SettingsPage     = lazy(() => import('./pages/SettingsPage'));

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
    localStorage.removeItem('user');
    localStorage.removeItem('auth_token');
  };

  // Register the force-logout callback so the axios 401 interceptor
  // can clear React state without window.location.reload()
  useEffect(() => {
    registerForceLogout(handleLogout);
  }, []);

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
            <UserContext.Provider value={{ currentUser, refreshUser, logout: handleLogout }}>
              <NotificationProvider>
                <Suspense fallback={
                  <div className="page-container fade-in" style={{ paddingTop: '2rem' }}>
                    <SkeletonLoader type="title" className="mb-4" />
                    <SkeletonLoader type="card" count={3} />
                  </div>
                }>
                  <Routes>
                    <Route path="/family-dashboard" element={<FamilyDashboardRoute />} />
                    <Route
                      path="/"
                      element={<DashboardLayout />}
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
                </Suspense>
              </NotificationProvider>
            </UserContext.Provider>
          )}
        </BrowserRouter>
      </ErrorBoundary>
    </ToastProvider>
  );
}

export default App;
