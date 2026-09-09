"""Checkpointed Studionet audit. Submitted hashes are never resent."""
import base64,getpass,hashlib,json,sys,time
from pathlib import Path
import requests
from genlayer_py import create_account,create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet
R=Path(__file__).resolve().parents[1];A='0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc';RPC='https://studio.genlayer.com/api';C='c8f3f47789acf6f44822f3620f7c96ad59ec9692';BASE=f'https://raw.githubusercontent.com/dearmore5382/RecallBatch-Boundary-Registry/{C}/test-fixtures';SH='bc4468e5d93b6682d40f511e6d09cba8cdb244027a91cf7c584ad40a908ec979';RC=(f'{BASE}/recall-eu.json','32f99914f57f2ad8c9aabbaaca8c17f2321065c68cbc4c7bb3250e12cfebdc5f');IN=(f'{BASE}/batch-affected.json','ca7f87b4b60e36e41afa96bfe28d8461a0d9e91e85a3573ce1bdd57c24f18c97');OUT=(f'{BASE}/batch-outside.json','705147b2db28a670f527e07e06d537173c46c1ac18c1ac34c6988476339aa466');P=R/'.private'/('recall-'+A.lower()+'.json');O=R/'verification'/('live-'+A.lower()+'.json')
def rpc(m,p):
 x=requests.post(RPC,json={'jsonrpc':'2.0','id':1,'method':m,'params':p},timeout=45);x.raise_for_status();d=x.json()
 if 'error'in d:raise RuntimeError(d['error'])
 return d['result']
def view(m,args=[]):
 d=serialize([calldata.encode({'method':m,'args':args}),b'\0']);r=rpc('gen_call',[{'type':'read','to':A,'from':'0x0000000000000000000000000000000000000001','value':'0x0','data':d,'transaction_hash_variant':'latest-final'}]);return str(calldata.decode(bytes.fromhex(r.removeprefix('0x'))))
def ret(t):
 r=t['consensus_data']['leader_receipt'];r=[r]if isinstance(r,dict)else r;r=[x for x in r if x.get('mode')=='leader'][-1];v=r['result'];z=base64.b64decode(v['raw']if isinstance(v,dict)else v)
 if r['execution_result']!='SUCCESS'or z[0]!=0:raise RuntimeError('EXECUTION_FAILED')
 return str(calldata.decode(z[1:]))
def save(j):
 P.parent.mkdir(exist_ok=True);P.write_text(json.dumps(j,indent=2));q=json.loads(json.dumps(j));[x.pop('receipt',None)for x in q['steps']];O.write_text(json.dumps(q,indent=2)+'\n')
def main():
 if not sys.stdin.isatty():raise RuntimeError('TTY_REQUIRED')
 keys=json.loads(getpass.getpass('TWO_TEST_KEYS_NO_ECHO: '));accounts=[create_account(account_private_key='0x'+x.removeprefix('0x'))for x in keys];del keys
 if len(accounts)!=2:raise RuntimeError('TWO_KEYS_REQUIRED')
 if hashlib.sha256((R/'contracts'/'RecallBatchBoundaryRegistry.py').read_bytes()).hexdigest()!=SH or base64.b64decode(rpc('gen_getContractCode',[A]))!=(R/'contracts'/'RecallBatchBoundaryRegistry.py').read_bytes():raise RuntimeError('SOURCE_MISMATCH')
 clients={x.address.lower():create_client(chain=studionet,account=x)for x in accounts};publisher,screener=accounts
 plan=[('F1-invalid-hash',publisher,'register_recall',[RC[0],'bad'],'INVALID_SOURCE_HASH'),('H1-register',publisher,'register_recall',[RC[0],RC[1]],'0'),('F2-outsider-activate',screener,'activate_recall',[0],'CREATOR_ONLY'),('H2-activate',publisher,'activate_recall',[0],'RECALL_ACTIVATED'),('H3-screen-affected',screener,'screen_batch',[0,IN[0],IN[1]],'0'),('H4-screen-outside',publisher,'screen_batch',[0,OUT[0],OUT[1]],'1'),('A1-duplicate',screener,'screen_batch',[0,IN[0],IN[1]],'DUPLICATE_SCREEN')]
 j=json.loads(P.read_text())if P.exists()else{'contract':A,'source_sha256':SH,'fixture_commit':C,'wallets':[x.address for x in accounts],'steps':[],'complete':False}
 if not P.exists()and view('get_counts')!='0|0':raise RuntimeError('EXPECTED_EMPTY_DEPLOYMENT')
 save(j);print(json.dumps({'ready':True,'completed':len(j['steps']),'total':len(plan)}),flush=True)
 for i,(name,actor,method,args,want)in enumerate(plan):
  if i<len(j['steps']):item=j['steps'][i]
  else:
   item={'id':name,'actor':actor.address,'method':method,'args':args,'expected':want,'status':'INTENT'};j['steps'].append(item);save(j);item['hash']=str(clients[actor.address.lower()].write_contract(address=A,function_name=method,args=args,value=0,leader_only=False));item['status']='SUBMITTED';save(j);print(json.dumps({'step':name,'hash':item['hash']}),flush=True)
  if item.get('status')=='VERIFIED':continue
  for _ in range(150):
   tx=rpc('eth_getTransactionByHash',[item['hash']])
   if tx and tx.get('status')=='FINALIZED':
    if tx.get('result_name')!='MAJORITY_AGREE':raise RuntimeError('CONSENSUS_FAILED:'+name)
    got=ret(tx)
    if got!=want:raise RuntimeError(f'UNEXPECTED:{name}:{got}')
    readback={'counts':view('get_counts'),'recall0':view('get_recall',[0]) if int(view('get_counts').split('|')[0]) else 'NOT_FOUND'}
    for sid in range(int(readback['counts'].split('|')[1])):readback[f'screen{sid}']=view('get_screen',[sid])
    item.update({'actual':got,'readback':readback,'receipt':tx,'status':'VERIFIED'});save(j);print(json.dumps({'step':name,'actual':got,'readback':readback}),flush=True);break
   time.sleep(8)
  else:raise RuntimeError('POLL_TIMEOUT_KEEP_HASH')
 j['complete']=True;save(j);print(json.dumps({'complete':True,'steps':len(plan)}))
if __name__=='__main__':main()
