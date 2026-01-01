import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ActionWatch/);
});

test('login flow (mocked)', async ({ page }) => {
    // Mock the /api/auth/me endpoint to simulate a logged-in user
    await page.route('**/api/auth/me', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                user: {
                    id: 1,
                    login: 'testuser',
                    avatar_url: 'https://github.com/testuser.png',
                    name: 'Test User'
                },
                installations: [
                    {
                        id: 123,
                        account_login: 'testorg',
                        account_avatar_url: 'https://github.com/testorg.png',
                        subscription: {
                            plan: 'free',
                            isPro: false
                        }
                    }
                ]
            })
        });
    });

    // Mock workflows endpoint
    await page.route('**/api/workflows/', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([])
        });
    });

    // Set the auth cookie
    await page.context().addCookies([
        {
            name: 'gh_token',
            value: 'mock-token',
            domain: 'localhost',
            path: '/'
        }
    ]);

    await page.goto('/');

    // Should be redirected to dashboard (or stay on dashboard if already there)
    // Verify dashboard loaded
    await expect(page).toHaveTitle(/ActionWatch/);
    await expect(page.getByText('ActionWatch')).toBeVisible();
    // Check if the organization switcher has the correct value selected
    await expect(page.getByRole('combobox')).toHaveValue('123');
});
