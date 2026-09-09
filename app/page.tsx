'use client';
import Image from 'next/image';
import { useState, type FormEvent } from 'react';
import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionHashVariant } from 'genlayer-js/types';
import {
  Activity,
  AlertTriangle,
  Boxes,
  CheckCircle2,
  FileCheck2,
  RefreshCw,
  Search,
  ShieldAlert,
  Wallet,
} from 'lucide-react';
import deployment from './deployment.json';
import {
  addressOK,
  digestOK,
  parseCounts,
  parseRecall,
  parseScreen,
  uint,
} from './protocol.mjs';
type Provider = NonNullable<Parameters<typeof createClient>[0]>['provider'];
const address = deployment.contractAddress as `0x${string}`,
  reader = createClient({ chain: studionet });
const configured =
    addressOK(address) && /^[a-f0-9]{64}$/.test(deployment.sourceSha256),
  writes = configured && deployment.liveAuditVerified;
const short = (v: string) =>
  v.length > 15 ? `${v.slice(0, 8)}…${v.slice(-5)}` : v;
export default function Page() {
  const [wallet, setWallet] = useState('');
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState(
    configured
      ? 'Registry online.'
      : 'Preview mode — deploy the reviewed contract to enable operations.',
  );
  const [recallId, setRecallId] = useState('0');
  const [screenId, setScreenId] = useState('0');
  const [recall, setRecall] = useState<ReturnType<typeof parseRecall> | null>(
    null,
  );
  const [screen, setScreen] = useState<ReturnType<typeof parseScreen> | null>(
    null,
  );
  const [counts, setCounts] = useState({ recalls: 0, screens: 0 });
  const err = (e: unknown) =>
    setNote(e instanceof Error ? e.message : 'Operation failed.');
  async function connect() {
    setBusy(true);
    try {
      if (!writes) throw new Error('Writes unlock after live verification.');
      const p = (window as unknown as { ethereum?: Provider }).ethereum;
      if (!p) throw new Error('Install an EIP-1193 wallet.');
      const a = (await p.request({
        method: 'eth_requestAccounts',
      })) as string[];
      await p.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${studionet.id.toString(16)}` }],
      });
      setWallet(a[0]);
      setNote('Wallet connected on Studionet.');
    } catch (e) {
      err(e);
    } finally {
      setBusy(false);
    }
  }
  async function read(name: string, args: bigint[] = []) {
    return reader.readContract({
      address,
      functionName: name,
      args,
      transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
    });
  }
  async function refresh() {
    setBusy(true);
    try {
      if (!configured) throw new Error('Deploy the reviewed contract first.');
      const c = parseCounts(await read('get_counts'));
      if (c) setCounts(c);
      setRecall(
        parseRecall(await read('get_recall', [uint(recallId, 'recall ID')])),
      );
      setScreen(
        parseScreen(await read('get_screen', [uint(screenId, 'screen ID')])),
      );
      setNote('Loaded finalized registry state.');
    } catch (e) {
      err(e);
    } finally {
      setBusy(false);
    }
  }
  async function send(method: string, args: (string | bigint | boolean)[]) {
    setBusy(true);
    try {
      if (!writes || !wallet)
        throw new Error('Connect a verified Studionet wallet first.');
      const p = (window as unknown as { ethereum?: Provider }).ethereum;
      if (!p) throw new Error('Wallet disconnected.');
      const w = createClient({
        chain: studionet,
        account: wallet as `0x${string}`,
        provider: p,
      });
      const hash = await w.writeContract({
        address,
        functionName: method,
        args,
        value: 0n,
        leaderOnly: false,
      });
      setNote(
        `Submitted ${short(String(hash))}. Wait for FINALIZED, then refresh; do not resubmit.`,
      );
    } catch (e) {
      err(e);
    } finally {
      setBusy(false);
    }
  }
  function register(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget),
      url = String(d.get('url')).trim(),
      sha = String(d.get('sha')).trim();
    if (!digestOK(sha))
      return setNote('Recall digest must be 64 hexadecimal characters.');
    void send('register_recall', [url, sha]);
  }
  function screenBatch(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget),
      url = String(d.get('url')).trim(),
      sha = String(d.get('sha')).trim();
    if (!digestOK(sha))
      return setNote('Batch digest must be 64 hexadecimal characters.');
    void send('screen_batch', [uint(recallId, 'recall ID'), url, sha]);
  }
  function role(e: FormEvent<HTMLFormElement>, method: string) {
    e.preventDefault();
    const d = new FormData(e.currentTarget),
      account = String(d.get('account')).trim();
    if (!addressOK(account))
      return setNote('Enter a valid non-zero account address.');
    void send(method, [account, String(d.get('allowed')) === 'true']);
  }
  function supersede(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    void send('supersede_recall', [
      uint(recallId, 'old recall ID'),
      uint(String(d.get('newId')), 'new recall ID'),
    ]);
  }
  return (
    <main className="ops">
      <header>
        <div className="identity">
          <Image
            src="/recallbatch-logo.png"
            width={52}
            height={52}
            alt="RecallBatch logo"
          />
          <div>
            <b>RecallBatch</b>
            <span>Boundary Registry</span>
          </div>
        </div>
        <nav>
          <span>
            <i />
            STUDIONET
          </span>
          <code>{configured ? short(address) : 'PRE-DEPLOYMENT'}</code>
        </nav>
        <button onClick={connect} disabled={busy || !writes}>
          <Wallet />
          {wallet ? short(wallet) : 'Connect wallet'}
        </button>
      </header>
      <section className="command">
        <div>
          <span>OPERATIONS / PRODUCT SAFETY</span>
          <h1>Recall control room</h1>
          <p>
            Activate one authenticated campaign. Screen many independent
            inventory batches against its fixed boundary.
          </p>
        </div>
        <button onClick={() => void refresh()} disabled={busy || !configured}>
          <RefreshCw />
          Sync registry
        </button>
      </section>
      <section className="metrics">
        <article>
          <Activity />
          <span>
            Active registry<b>{configured ? 'ONLINE' : 'PREVIEW'}</b>
          </span>
        </article>
        <article>
          <FileCheck2 />
          <span>
            Recall campaigns<b>{counts.recalls}</b>
          </span>
        </article>
        <article>
          <Boxes />
          <span>
            Batch screens<b>{counts.screens}</b>
          </span>
        </article>
        <article>
          <ShieldAlert />
          <span>
            Decision scope<b>BOUNDARY ONLY</b>
          </span>
        </article>
      </section>
      <section className="governance">
        <div>
          <span>TRUST CONTROL</span>
          <h2>Explicit authority registry</h2>
          <p>
            The owner grants or revokes publisher and batch-attestor roles.
            Hashes prove integrity; roles establish who is authorized to make
            each claim.
          </p>
        </div>
        <form onSubmit={(e) => role(e, 'set_publisher')}>
          <label>
            Publisher address
            <input name="account" placeholder="0x…" required />
          </label>
          <select name="allowed">
            <option value="true">Grant publisher</option>
            <option value="false">Revoke publisher</option>
          </select>
          <button disabled={!writes || busy}>Update publisher</button>
        </form>
        <form onSubmit={(e) => role(e, 'set_attestor')}>
          <label>
            Batch attestor address
            <input name="account" placeholder="0x…" required />
          </label>
          <select name="allowed">
            <option value="true">Grant attestor</option>
            <option value="false">Revoke attestor</option>
          </select>
          <button disabled={!writes || busy}>Update attestor</button>
        </form>
      </section>
      <section className="grid">
        <article className="campaign">
          <div className="panel-title">
            <span>01</span>
            <div>
              <b>Recall campaigns</b>
              <small>Publisher-controlled activation and correction</small>
            </div>
          </div>
          <form onSubmit={register}>
            <label>
              Recall JSON URL
              <input
                name="url"
                type="url"
                placeholder="https://raw.githubusercontent.com/…"
                required
              />
            </label>
            <label>
              SHA-256 digest
              <input
                name="sha"
                pattern="[0-9a-fA-F]{64}"
                placeholder="64 hexadecimal characters"
                required
              />
            </label>
            <button disabled={!writes || busy}>Register campaign</button>
          </form>
          <div className="record">
            <label>
              Recall ID
              <input
                value={recallId}
                onChange={(e) => setRecallId(e.target.value)}
              />
            </label>
            <div className="actions">
              <button onClick={() => void send('activate_recall', [uint(recallId, 'recall ID')])} disabled={!writes || busy}>Activate</button>
              <button onClick={() => void send('suspend_recall', [uint(recallId, 'recall ID')])} disabled={!writes || busy}>Suspend</button>
            </div>
            <dl>
              <dt>State</dt>
              <dd>{recall?.state ?? 'Not loaded'}</dd>
              <dt>Publisher</dt>
              <dd>{recall ? short(recall.creator) : '—'}</dd>
              <dt>Superseded by</dt>
              <dd>{recall?.supersededBy ?? '—'}</dd>
            </dl>
            <form className="supersede" onSubmit={supersede}>
              <label>Replacement recall ID<input name="newId" inputMode="numeric" required /></label>
              <button disabled={!writes || busy}>Supersede selected recall</button>
            </form>
          </div>
        </article>
        <article className="screening">
          <div className="panel-title">
            <span>02</span>
            <div>
              <b>Inventory screening</b>
              <small>Authorized attestors with issuer-bound records</small>
            </div>
          </div>
          <form onSubmit={screenBatch}>
            <label>
              Batch record JSON URL
              <input
                name="url"
                type="url"
                placeholder="https://raw.githubusercontent.com/…"
                required
              />
            </label>
            <label>
              SHA-256 digest
              <input
                name="sha"
                pattern="[0-9a-fA-F]{64}"
                placeholder="64 hexadecimal characters"
                required
              />
            </label>
            <button disabled={!writes || busy}>
              <Search />
              Screen against recall {recallId}
            </button>
          </form>
          <div className="record">
            <label>
              Screen ID
              <input
                value={screenId}
                onChange={(e) => setScreenId(e.target.value)}
              />
            </label>
            <dl>
              <dt>Batch reference</dt>
              <dd>{screen?.batchRef ?? '—'}</dd>
              <dt>Submitted by</dt>
              <dd>{screen ? short(screen.screener) : '—'}</dd>
            </dl>
          </div>
        </article>
      </section>
      <section className={`outcome ${screen?.verdict?.toLowerCase() ?? ''}`}>
        <div>
          <span>LATEST LOADED SCREEN</span>
          <h2>{screen?.verdict ?? 'NO RESULT LOADED'}</h2>
          <p>
            {screen?.reason?.replaceAll('_', ' ').toLowerCase() ??
              'Load a finalized screen record to inspect its authoritative outcome.'}
          </p>
        </div>
        {screen?.verdict === 'AFFECTED' ? <AlertTriangle /> : <CheckCircle2 />}
      </section>
      <aside className="notice">
        <output>{note}</output>
        <p>
          Exact-source authentication precedes screening. Natural-language AI is
          restricted to an optional qualifier; structured lot, product,
          manufacturer, and region boundaries are deterministic.
        </p>
      </aside>
      <footer>
        <b>RecallBatch Boundary Registry</b>
        <span>
          Not a safety, liability, refund, disposal, or legal determination.
        </span>
      </footer>
    </main>
  );
}
