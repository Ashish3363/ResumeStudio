import { execFileSync } from 'node:child_process';
import path from 'node:path';

/**
 * Global setup: runs once before the whole suite.
 *
 * Delegates to `scripts/init_test_db.py` (using the backend venv) to create the
 * test database if needed, create the schema, and truncate all tables. Runs
 * before Playwright starts the web server, so the app boots against a clean DB.
 */

const BACKEND_DIR = path.resolve(__dirname, '..');
const PY = path.join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe');
const TEST_DATABASE_URL =
  'postgresql+psycopg://postgres:root@localhost:5432/resumeStudio_test';

export default async function globalSetup() {
  execFileSync(PY, ['scripts/init_test_db.py'], {
    cwd: BACKEND_DIR,
    stdio: 'inherit',
    env: { ...process.env, DATABASE_URL: TEST_DATABASE_URL },
  });
}
