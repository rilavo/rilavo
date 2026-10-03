/** Smoke test for TypeScript SDK */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { runSmoke } from '../src/smoke.js';

test('runSmoke() returns ok=true with 3 expected steps', async () => {
  const result = await runSmoke();
  assert.equal(result.ok, true, 'smoke should pass');
  assert.ok(result.steps.length >= 3, 'should have at least 3 steps');
  
  // Check expected step patterns
  const stepStr = result.steps.join(' ');
  assert.ok(stepStr.includes('issue: OK'), 'should have issue step');
  assert.ok(stepStr.includes('verify accept: OK'), 'should have verify accept step');
  assert.ok(stepStr.includes('scope mismatch rejected: TRUE'), 'should have scope mismatch rejection');
  assert.ok(stepStr.includes('wrong audience rejected: TRUE'), 'should have audience mismatch rejection');
});

test('runSmoke() returns structured result', async () => {
  const result = await runSmoke();
  assert.ok(typeof result.ok === 'boolean', 'ok should be boolean');
  assert.ok(Array.isArray(result.steps), 'steps should be array');
  assert.ok(result.steps.every(s => typeof s === 'string'), 'all steps should be strings');
});