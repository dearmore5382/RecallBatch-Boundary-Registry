import test from 'node:test';
import assert from 'node:assert/strict';
import {
  addressOK,
  digestOK,
  parseRecall,
  parseScreen,
  parseCounts,
  parseRole,
  uint,
  finalStage,
} from '../app/protocol.mjs';
const a = '0x1111111111111111111111111111111111111111',
  d = 'a'.repeat(64);
test('identifiers are strict', () => {
  assert.ok(addressOK(a));
  assert.ok(digestOK(d));
  assert.equal(uint('9'), 9n);
  assert.throws(() => uint('-1'));
});
test('campaign and screen readback parsers reject malformed data', () => {
  assert.equal(
    parseRecall(`ACTIVE|${a}|https://x/r|${d}|NONE`).state,
    'ACTIVE',
  );
  assert.equal(
    parseScreen(`0|${a}|B-1|https://x/b|${d}|0:${d}|AFFECTED|WITHIN`).verdict,
    'AFFECTED',
  );
  assert.throws(() => parseScreen('bad'));
});
test('roles are explicit', () => {
  assert.deepEqual(parseRole('OWNER|True|True'), {
    owner: true,
    publisher: true,
    attestor: true,
  });
});
test('counts and finality parse', () => {
  assert.deepEqual(parseCounts('2|7'), { recalls: 2, screens: 7 });
  assert.equal(finalStage({ status: 'PROPOSING' }).stage, 'PENDING');
  assert.equal(
    finalStage({
      status: 'FINALIZED',
      consensus_data: {
        leader_receipt: {
          execution_result: 'SUCCESS',
          result: { status: 'return' },
        },
      },
    }).stage,
    'READBACK_REQUIRED',
  );
});
