export const ZERO = `0x${'0'.repeat(40)}`;
export const addressOK = (v) =>
  typeof v === 'string' &&
  /^0x[0-9a-fA-F]{40}$/.test(v) &&
  v.toLowerCase() !== ZERO;
export const digestOK = (v) =>
  typeof v === 'string' && /^[0-9a-fA-F]{64}$/.test(v);
export const txHashOK = (v) =>
  typeof v === 'string' && /^0x[0-9a-fA-F]{64}$/.test(v);
export function uint(v, label = 'ID') {
  const t = String(v);
  if (!/^(0|[1-9]\d*)$/.test(t) || BigInt(t) >= 2n ** 256n)
    throw new Error(`Enter an unsigned ${label}.`);
  return BigInt(t);
}
export function parseRecall(raw) {
  if (typeof raw !== 'string' || raw === 'NOT_FOUND')
    throw new Error('Recall not found.');
  const p = raw.split('|');
  if (p.length !== 5 || !addressOK(p[1]) || !digestOK(p[3]))
    throw new Error('Malformed recall readback.');
  return {
    state: p[0],
    creator: p[1],
    url: p[2],
    sha256: p[3],
    supersededBy: p[4],
  };
}
export function parseScreen(raw) {
  if (typeof raw !== 'string' || raw === 'NOT_FOUND')
    throw new Error('Screen not found.');
  const p = raw.split('|');
  if (
    p.length !== 8 ||
    !addressOK(p[1]) ||
    !digestOK(p[4]) ||
    !digestOK(p[5].split(':').at(-1))
  )
    throw new Error('Malformed screen readback.');
  return {
    recallId: p[0],
    screener: p[1],
    batchRef: p[2],
    url: p[3],
    sha256: p[4],
    canonicalKey: p[5],
    verdict: p[6],
    reason: p[7],
  };
}
export function parseRole(raw) {
  const p = String(raw).split('|');
  if (p.length !== 3) return null;
  return {
    owner: p[0] === 'OWNER',
    publisher: p[1] === 'True',
    attestor: p[2] === 'True',
  };
}
export function parseCounts(raw) {
  const p = String(raw).split('|');
  if (p.length !== 2) return null;
  return { recalls: Number(uint(p[0])), screens: Number(uint(p[1])) };
}
export function finalStage(tx) {
  const status = String(tx?.statusName ?? tx?.status ?? 'UNKNOWN');
  if (status !== 'FINALIZED') return { stage: 'PENDING', detail: status };
  const rs = tx?.consensus_data?.leader_receipt;
  const leader = Array.isArray(rs) ? rs.at(-1) : rs;
  if (
    !leader ||
    leader.execution_result !== 'SUCCESS' ||
    leader.result?.status !== 'return'
  )
    return {
      stage: 'FAILED',
      detail: 'Finalized without successful execution.',
    };
  return {
    stage: 'READBACK_REQUIRED',
    detail: 'Finalized; verify contract state.',
  };
}
