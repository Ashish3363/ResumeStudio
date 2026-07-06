import { defineConfig } from '@playwright/test';
import path from 'node:path';

/**
 * Playwright configuration for the ResumeStudio backend API tests.
 *
 * These are HTTP/API tests (no browser): each test uses Playwright's `request`
 * fixture to hit the live FastAPI app. Playwright itself starts the server
 * (see `webServer`) against a DEDICATED test database, so the dev DB is never
 * touched.
 */

const BACKEND_DIR = path.resolve(__dirname, '..');
const PY = path.join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe');

// Dedicated test DB — created/reset in global-setup.ts, used by the server below.
const TEST_DATABASE_URL =
  'postgresql+psycopg://postgres:root@localhost:5432/resumeStudio_test';

export default defineConfig({
  testDir: './tests',
  // Auth tests share one database; run them serially for predictable state.
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  globalSetup: './global-setup.ts',
  use: {
    baseURL: 'http://127.0.0.1:8000',
    extraHTTPHeaders: { 'Content-Type': 'application/json' },
  },
  webServer: {
    // Start uvicorn from the backend dir using the project's venv interpreter.
    command: `"${PY}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000`,
    cwd: BACKEND_DIR,
    url: 'http://127.0.0.1:8000/health',
    // Always start our own server so it's bound to the TEST database, not
    // whatever a developer might have running on :8000.
    reuseExistingServer: false,
    timeout: 60_000,
    env: { DATABASE_URL: TEST_DATABASE_URL },
  },
});
