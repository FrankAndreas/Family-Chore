import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';
import { login, newPerson } from './helpers';

// Accessibility review 2026-11-08: axe finds nothing on any page, for a parent and a child, on the tablet and a phone,
// so a change that breaks a label, a contrast, a landmark or a heading fails here
async function noViolations(page: Page, state: string) {
    // Loaded: the page's heading is there and the skeletons are gone
    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
    await expect(page.locator('.skeleton')).toHaveCount(0);
    // Cards that slide or fade in: measured once they're there (a spinner or a pulsing dot runs for ever, not waited for)
    await page.waitForFunction(() => document.getAnimations().every(a =>
        a.playState !== 'running' || a.effect?.getTiming().iterations === Infinity));
    const { violations } = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'])
        .analyze();
    expect(violations.map(v => `${v.id}: ${v.nodes.map(n => n.target.join(' ')).join(', ')}`), state).toEqual([]);
}

test('a parent\'s pages', async ({ page, request }) => {
    test.setTimeout(120_000);
    const errors = await login(page, await newPerson(request, 'PARENT'));
    await expect(page).toHaveURL(/\/admin$/);
    for (const path of ['/admin', '/admin/users', '/admin/tasks', '/admin/roles', '/admin/analytics', '/dashboard', '/rewards', '/settings', '/family-dashboard']) {
        await page.goto(path);
        await noViolations(page, path);
    }
    expect(errors).toEqual([]);
});

test('a child\'s pages', async ({ page, request }) => {
    const errors = await login(page, await newPerson(request, 'CHILD'), '/dashboard');
    for (const path of ['/dashboard', '/rewards', '/settings']) {
        await page.goto(path);
        await noViolations(page, path);
    }
    expect(errors).toEqual([]);
});

// An unknown address: the page that says so, not a crash (it read the dashboard layout's context, which isn't there)
test('an unknown address', async ({ page, request }) => {
    const errors = await login(page, await newPerson(request, 'PARENT'), '/nowhere');
    await expect(page.getByRole('heading', { name: /404/ })).toBeVisible();
    await noViolations(page, '404');
    await page.getByRole('button', { name: /Take Me Home/ }).click();
    await expect(page).toHaveURL(/\/admin$/);
    expect(errors).toEqual([]);
});

// The menu and the family dashboard's tabs say which is shown, not only by colour
test('the page and the tab shown are said', async ({ page, request }, info) => {
    test.skip(info.project.name === 'phone', 'the phone menu is a drawer');
    await login(page, await newPerson(request, 'PARENT'), '/admin/users');
    await expect(page.locator('.nav-item[aria-current="page"]')).toHaveCount(1);
    await page.goto('/family-dashboard');
    const rewards = page.getByRole('button', { name: /Rewards/ });
    await rewards.click();
    await expect(rewards).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByRole('button', { name: /Tasks/ }).first()).toHaveAttribute('aria-pressed', 'false');
});
