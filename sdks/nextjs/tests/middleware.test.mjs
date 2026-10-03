import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

describe('Rilavo Next.js Middleware', () => {
  test('middleware loads correctly', async () => {
    const { createMiddleware } = await import('../src/index.js');
    assert.ok(typeof createMiddleware === 'function');
  });
});
