import path from 'node:path';
import { expect, request as playwrightRequest, type APIRequestContext, type Page } from '@playwright/test';

// The Python with the backend's packages; a path is made absolute (Python warns about relative ones with "..")
const configured = process.env.E2E_PYTHON ?? 'python3';
export const PYTHON = configured.includes('/') ? path.resolve(configured) : configured;

export const HUB = 'http://localhost:8170';
export const FRONTEND = 'http://localhost:3150';
// The hub takes changes only with its own header
const HUB_HEADERS = { 'X-Requested-With': 'hub' };
const ADMIN_PIN = '1111';
const PIN = '1234';

// A login at the hub, in a throwaway API context: its cookies (hub_session, and hub_manage to change things there)
async function hubCookies(name: string, pin: string): Promise<{ token: string; cookies: string }> {
    const context = await playwrightRequest.newContext();
    try {
        const response = await context.post(`${HUB}/api/login`, { data: { name, pin }, headers: HUB_HEADERS });
        expect(response.ok(), await response.text()).toBeTruthy();
        const found = response.headersArray()
            .filter(h => h.name.toLowerCase() === 'set-cookie' && /^hub_(session|manage)=/.test(h.value))
            .map(h => h.value.split(';')[0]);
        const session = found.find(c => c.startsWith('hub_session='));
        expect(session, 'the hub sets hub_session').toBeTruthy();
        return { token: session!.slice('hub_session='.length), cookies: found.join('; ') };
    } finally {
        await context.dispose();
    }
}

async function asHubAdmin<T = any>(request: APIRequestContext, method: string, path: string, data?: unknown): Promise<T> {
    const { cookies } = await hubCookies('Admin', ADMIN_PIN);
    const response = await request.fetch(`${HUB}${path}`, { method, data, headers: { ...HUB_HEADERS, Cookie: cookies } });
    expect(response.ok(), `${method} ${path}: ${await response.text()}`).toBeTruthy();
    return response.json();
}

// A person of the test's own in the hub, with access to this app (the hub tile with the key "chores", made on first
// use); returns their hub login. Invented names only: the repository is public
export async function newPerson(request: APIRequestContext, role: 'PARENT' | 'CHILD' = 'PARENT'): Promise<{ name: string; token: string }> {
    const name = `${role === 'PARENT' ? 'Eli' : 'Kim'}${Date.now().toString(36).slice(-4)}${Math.random().toString(36).slice(2, 5)}`;
    const person = await asHubAdmin(request, 'POST', '/api/people', { name, pin: PIN, role });
    const tiles = await asHubAdmin<{ id: number; app_key: string | null; people: number[] }[]>(request, 'GET', '/api/tiles/manage');
    let tile = tiles.find(t => t.app_key === 'chores');
    if (!tile) tile = await asHubAdmin(request, 'POST', '/api/tiles', { name: 'Ämtli', local_url: FRONTEND, app_key: 'chores' });
    await asHubAdmin(request, 'PATCH', `/api/tiles/${tile!.id}`, { people: [...new Set([...tile!.people, person.id])] });
    const { token } = await hubCookies(name, PIN);
    return { name, token };
}

// Logged in as at home: the hub's cookie in the browser. Collects errors in the browser console for the test to check
export async function login(page: Page, person: { token: string }, path = '/'): Promise<string[]> {
    const errors: string[] = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    await page.context().addCookies([{ name: 'hub_session', value: person.token, url: FRONTEND }]);
    await page.goto(path);
    return errors;
}
