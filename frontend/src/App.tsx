import { useState, useEffect, lazy, Suspense } from 'react';
import { ToastProvider } from './context/ToastContext';
import { NotificationProvider } from './context/NotificationContext';
import { UserContext } from './context/UserContext';
import ErrorBoundary from './components/ErrorBoundary';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import NoAccess from './components/NoAccess';
import DashboardLayout from './layouts/DashboardLayout';
import FamilyDashboardView from './components/FamilyDashboard';
import NotFoundPage from './pages/NotFoundPage';
import { SkeletonLoader } from './components/SkeletonLoader';
import type { User } from './types';
import i18n from './i18n';
import { getMe, goToHubLogout } from './api';
import { ADMIN_ROLE_NAME } from './constants';
import './App.css';
import './index.css';

// Route-level code-splitting: each page loads as a separate JS chunk on first navigation.
// DashboardLayout, FamilyDashboardView, and ErrorBoundary are kept eager
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

// in: logged in; no_access: logged in at the family hub, but not given this app; hub_unavailable: the hub (or the NAS)
// doesn't answer; away: on the way to the hub's login (the API's 401 sends the browser there)
type AuthState = 'loading' | 'in' | 'no_access' | 'hub_unavailable' | 'away';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [state, setState] = useState<AuthState>('loading');
  const [attempt, setAttempt] = useState(0);

  // Who is logged in: the family hub's login (spec 2026-10-30); the backend asks the hub. The family dashboard
  // works without a login, so this asks without being sent to the hub
  useEffect(() => {
    if (window.location.pathname.startsWith('/family-dashboard')) return;
    getMe()
      .then((res) => {
        setCurrentUser(res.data);
        // The language follows the person (from the hub)
        if (res.data.preferred_language) void i18n.changeLanguage(res.data.preferred_language);
        setState('in');
      })
      .catch((err) => {
        const status = err.response?.status;
        const code = err.response?.data?.detail;
        setState(code === 'no_access' ? 'no_access' : status === 401 ? 'away' : 'hub_unavailable');
      });
  }, [attempt]);

  // "Log out" ends the login in the family hub, for every family app
  const handleLogout = () => {
    void goToHubLogout();
  };

  const refreshUser = async () => {
    try {
      setCurrentUser((await getMe()).data);
    } catch (err) {
      console.error('Failed to refresh user', err);
    }
  };

  const retry = () => {
    setState('loading');
    setAttempt((n) => n + 1);
  };

  return (
    <ToastProvider>
      <ErrorBoundary>
        <BrowserRouter>
          {!currentUser ? (
            <Routes>
              <Route path="/family-dashboard" element={<FamilyDashboardRoute />} />
              <Route
                path="*"
                element={
                  state === 'no_access' || state === 'hub_unavailable'
                    ? <NoAccess hubDown={state === 'hub_unavailable'} onRetry={retry} onLogout={handleLogout} />
                    : <SkeletonLoader type="card" count={1} />
                }
              />
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
                      element={<Navigate to={currentUser.role.name === ADMIN_ROLE_NAME ? '/admin' : '/dashboard'} replace />}
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
