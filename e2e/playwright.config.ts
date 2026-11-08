import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';
import { PYTHON as python } from './tests/helpers';

// The tests start their own family hub (Admin PIN 1111), backend (fresh SQLite database) and frontend, on ports of their
// own, so a dev server and its data are never touched. E2E_PYTHON: the Python with the backend's packages. HUB_DIR: a
// family-hub checkout (default: next to this repo); HUB_PYTHON: the Python with the hub's packages (default: E2E_PYTHON)
export const BACKEND = 'http://localhost:8160';
export const FRONTEND = 'http://localhost:3150';
export const HUB = 'http://localhost:8170';
const tmp = path.resolve(__dirname, '.tmp');
const hubData = path.join(tmp, 'hub');
const database = path.join(tmp, 'e2e.db');
const hubDir = path.resolve(process.env.HUB_DIR ?? path.join(__dirname, '..', '..', 'family-hub'));
const hubPython = process.env.HUB_PYTHON ? path.resolve(process.env.HUB_PYTHON) : python;

export default defineConfig({
    testDir: './tests',
    // One backend and database for all tests; each test works with people of its own
    workers: 1,
    retries: process.env.CI ? 1 : 0,
    reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
    use: {
        baseURL: FRONTEND,
        locale: 'en-US',
        trace: 'retain-on-failure',
        screenshot: 'only-on-failure',
    },
    projects: [
        { name: 'tablet', use: { ...devices['Desktop Chrome'], viewport: { width: 1180, height: 820 } } },
        { name: 'phone', use: { ...devices['Pixel 7'] } },
    ],
    webServer: [
        {
            // The family hub: people, PINs and the login
            command: `rm -rf "${hubData}" && mkdir -p "${hubData}" && "${hubPython}" -m uvicorn app.main:app --port 8170`,
            cwd: path.join(hubDir, 'backend'),
            url: `${HUB}/health`,
            env: {
                DATABASE_URL: `sqlite:///${hubData}/hub.db`,
                DATA_DIR: hubData,
                INITIAL_ADMIN_PIN: '1111',
                DEFAULT_LANGUAGE: 'en',
                // Plain http in the tests: a Secure cookie would never come back
                COOKIE_INSECURE: '1',
            },
            reuseExistingServer: false,
            timeout: 60_000,
        },
        {
            // TESTING: tables made directly (no migrations) and no rate limits
            command: `mkdir -p "${tmp}" && rm -f "${database}" && "${python}" -m uvicorn backend.main:app --port 8160`,
            cwd: path.resolve(__dirname, '..'),
            url: `${BACKEND}/docs`,
            env: {
                TESTING: 'True',
                DATABASE_URL: `sqlite:///${database}`,
                HUB_URL: HUB,
                HUB_PUBLIC_URL: HUB,
                CORS_ORIGINS: FRONTEND,
            },
            reuseExistingServer: false,
            timeout: 60_000,
        },
        {
            command: 'npx vite --port 3150 --strictPort',
            cwd: path.resolve(__dirname, '..', 'frontend'),
            url: FRONTEND,
            // The hub's cookie is for localhost, so the browser sends it to the backend's port too (as at home, where
            // it is for local.<domain>)
            env: { VITE_API_BASE_URL: BACKEND },
            reuseExistingServer: false,
            timeout: 60_000,
        },
    ],
});
