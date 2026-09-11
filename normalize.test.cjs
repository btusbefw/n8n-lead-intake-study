const { test } = require('node:test');
const assert = require('node:assert/strict');
const { normalize } = require('./normalize.cjs');
const valid = { requestId: 'demo-1', name: ' Ana Demo ', email: 'ANA@example.test', ignoredSecret: 'must-not-leave' };
test('allowlists fields and normalizes submitted text', () => {
  assert.deepEqual(normalize([valid]).accepted, [{ externalId: 'demo-1', name: 'Ana Demo', email: 'ana@example.test', source: 'demo-form' }]);
});
test('invalid records never become CRM writes', () => {
  const result = normalize([null, [], { ...valid, requestId: '../bad' }, { ...valid, email: 'bad' }, { ...valid, name: '' }]);
  assert.equal(result.accepted.length, 0);
  assert.deepEqual(result.rejected.map(x => x.reason), ['invalid_object','invalid_object','invalid_request_id','invalid_email','invalid_name']);
});
test('duplicate source IDs are rejected within the batch without dropping distinct requests', () => {
  const result = normalize([valid, valid, { ...valid, requestId: 'demo-2' }]);
  assert.equal(result.accepted.length, 2);
  assert.deepEqual(result.rejected, [{ index: 1, reason: 'duplicate_request_id' }]);
});
test('invalid first occurrence does not suppress a corrected record', () => {
  assert.equal(normalize([{ ...valid, email: 'bad' }, valid]).accepted.length, 1);
});
