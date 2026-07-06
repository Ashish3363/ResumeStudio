import { test, expect, APIRequestContext } from '@playwright/test';

/**
 * End-to-end API tests for the JWT auth slice.
 *
 * Every request goes over real HTTP to the running FastAPI app (started by
 * Playwright against the test database). Tests use freshly-generated unique
 * emails so they don't collide with each other, which keeps them independent
 * without needing per-test DB cleanup.
 */

/** A unique email per call, so tests never collide on the users.email UNIQUE. */
function uniqueEmail(tag = 'user'): string {
  return `e2e_${tag}_${Date.now()}_${Math.floor(Math.random() * 1e6)}@example.com`;
}

/** Register + log in a brand-new user; returns their email + token pair. */
async function registerAndLogin(request: APIRequestContext, password = 'secret123') {
  const email = uniqueEmail();
  const reg = await request.post('/api/auth/register', {
    data: { email, password, full_name: 'E2E User' },
  });
  expect(reg.status(), 'register should succeed').toBe(201);

  const login = await request.post('/api/auth/login', { data: { email, password } });
  expect(login.status(), 'login should succeed').toBe(200);

  const tokens = await login.json();
  return { email, password, ...tokens } as {
    email: string;
    password: string;
    access_token: string;
    refresh_token: string;
    token_type: string;
  };
}

test.describe('auth', () => {
  test('register returns a safe user view and no secrets (201)', async ({ request }) => {
    const email = uniqueEmail();
    const res = await request.post('/api/auth/register', {
      data: { email, password: 'secret123', full_name: 'Jane Doe' },
    });
    expect(res.status()).toBe(201);

    const body = await res.json();
    expect(body.email).toBe(email);
    expect(body.full_name).toBe('Jane Doe');
    expect(body.plan).toBe('free');
    expect(body.is_email_verified).toBe(false);
    expect(body).toHaveProperty('id');
    // UserOut must never expose these:
    expect(body).not.toHaveProperty('password_hash');
    expect(body).not.toHaveProperty('token_version');
  });

  test('duplicate email is rejected (409 email_exists)', async ({ request }) => {
    const email = uniqueEmail();
    await request.post('/api/auth/register', { data: { email, password: 'secret123' } });

    const dup = await request.post('/api/auth/register', { data: { email, password: 'secret123' } });
    expect(dup.status()).toBe(409);
    expect((await dup.json()).code).toBe('email_exists');
  });

  test('too-short password is rejected by validation (422)', async ({ request }) => {
    const res = await request.post('/api/auth/register', {
      data: { email: uniqueEmail(), password: 'short' }, // < 8 chars
    });
    expect(res.status()).toBe(422);
  });

  test('login returns an access + refresh token pair', async ({ request }) => {
    const { access_token, refresh_token, token_type } = await registerAndLogin(request);
    expect(access_token).toBeTruthy();
    expect(refresh_token).toBeTruthy();
    expect(token_type).toBe('bearer');
  });

  test('login with a wrong password is 401 invalid_credentials', async ({ request }) => {
    const { email } = await registerAndLogin(request);
    const res = await request.post('/api/auth/login', { data: { email, password: 'wrong-password' } });
    expect(res.status()).toBe(401);
    expect((await res.json()).code).toBe('invalid_credentials');
  });

  test('login with an unknown email is 401 (no user enumeration)', async ({ request }) => {
    const res = await request.post('/api/auth/login', {
      data: { email: uniqueEmail(), password: 'secret123' },
    });
    expect(res.status()).toBe(401);
    expect((await res.json()).code).toBe('invalid_credentials');
  });

  test('/me requires a bearer token (401)', async ({ request }) => {
    const res = await request.get('/api/auth/me');
    expect(res.status()).toBe(401);
    expect((await res.json()).code).toBe('invalid_token');
  });

  test('/me with a valid access token returns the current user', async ({ request }) => {
    const { email, access_token } = await registerAndLogin(request);
    const res = await request.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(res.status()).toBe(200);
    expect((await res.json()).email).toBe(email);
  });

  test('refresh issues new tokens that work', async ({ request }) => {
    const { refresh_token } = await registerAndLogin(request);
    const res = await request.post('/api/auth/refresh', { data: { refresh_token } });
    expect(res.status()).toBe(200);

    const fresh = await res.json();
    expect(fresh.access_token).toBeTruthy();
    // the newly-minted access token should authenticate /me
    const me = await request.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${fresh.access_token}` },
    });
    expect(me.status()).toBe(200);
  });

  test('an access token cannot be used as a refresh token (401)', async ({ request }) => {
    const { access_token } = await registerAndLogin(request);
    const res = await request.post('/api/auth/refresh', { data: { refresh_token: access_token } });
    expect(res.status()).toBe(401);
    expect((await res.json()).code).toBe('invalid_token');
  });

  test('an invalid/garbage bearer token is rejected (401)', async ({ request }) => {
    const res = await request.get('/api/auth/me', {
      headers: { Authorization: 'Bearer not-a-real-jwt' },
    });
    expect(res.status()).toBe(401);
    expect((await res.json()).code).toBe('invalid_token');
  });

  test('logout revokes all outstanding tokens (access + refresh)', async ({ request }) => {
    const { access_token, refresh_token } = await registerAndLogin(request);

    const out = await request.post('/api/auth/logout', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(out.status()).toBe(204);

    // The old access token no longer authenticates.
    const me = await request.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(me.status()).toBe(401);

    // The old refresh token is dead too (token_version was bumped).
    const ref = await request.post('/api/auth/refresh', { data: { refresh_token } });
    expect(ref.status()).toBe(401);
  });
});
