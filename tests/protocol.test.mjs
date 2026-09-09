import test from'node:test';import assert from'node:assert/strict';import{addressOK,digestOK,parseRecall,parseScreen,parseCounts,uint,finalStage}from'../app/protocol.mjs';
const a='0x1111111111111111111111111111111111111111',d='a'.repeat(64);
test('identifiers are strict',()=>{assert.ok(addressOK(a));assert.ok(digestOK(d));assert.equal(uint('9'),9n);assert.throws(()=>uint('-1'))});
test('campaign and screen readback parsers reject malformed data',()=>{assert.equal(parseRecall(`ACTIVE|${a}|https://x/r|${d}`).state,'ACTIVE');assert.equal(parseScreen(`0|${a}|B-1|https://x/b|${d}|AFFECTED|WITHIN`).verdict,'AFFECTED');assert.throws(()=>parseScreen('bad'))});
test('counts and finality parse',()=>{assert.deepEqual(parseCounts('2|7'),{recalls:2,screens:7});assert.equal(finalStage({status:'PROPOSING'}).stage,'PENDING');assert.equal(finalStage({status:'FINALIZED',consensus_data:{leader_receipt:{execution_result:'SUCCESS',result:{status:'return'}}}}).stage,'READBACK_REQUIRED')});
