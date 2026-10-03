/** Doctor test for TypeScript SDK */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { runDoctor } from '../src/doctor.js';

test('runDoctor() returns structured result', async () => {
  const result = await runDoctor();
  
  assert.ok(typeof result.ok === 'boolean', 'ok should be boolean');
  assert.ok(Array.isArray(result.checks), 'checks should be array');
  
  // Should have expected checks (matching actual implementation)
  const names = result.checks.map(c => c.name);
  assert.ok(names.includes('import @rilavo/sdk'), 'should check import');
  assert.ok(names.includes('runSmoke exported'), 'should check runSmoke exported');
  assert.ok(names.includes('runDoctor exported'), 'should check runDoctor exported');
  assert.ok(names.includes('verifyCredential exported'), 'should check verifyCredential exported');
  assert.ok(names.includes('issueCredential exported'), 'should check issueCredential exported');
  
  // ok should be boolean
  assert.ok(typeof result.ok === 'boolean', 'ok should be boolean');
});

test('runDoctor() online flag accepted', async () => {
  const result = await runDoctor(true);
  assert.ok(typeof result.ok === 'boolean', 'ok should be boolean');
});