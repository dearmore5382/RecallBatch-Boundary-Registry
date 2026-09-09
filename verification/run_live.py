"""Checkpointed hardened-release Studionet audit; never resends a saved hash."""
import base64,getpass,hashlib,json,sys,time
from pathlib import Path
import requests
from genlayer_py import create_account,create_client
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.chains import studionet
R=Path(__file__).resolve().parents[1];A='0x1E09EDDbd1dde3eC95f150D02304f542d511132F';RPC='https://studio.genlayer.com/api';C='a7a2a800a45553fed12ab75b9affd46ed79c0f11';BASE=f'https://raw.githubusercontent.com/dearmore5382/RecallBatch-Boundary-Registry/{C}/test-fixtures';SH='48ae82af9846e4e9fcfed307483bfab4ee448da0a9e5dda2cf01087aedfc5378';RC=(f'{BASE}/recall-eu.json','32f99914f57f2ad8c9aabbaaca8c17f2321065c68cbc4c7bb3250e12cfebdc5f');IN=(f'{BASE}/batch-affected.json','00f8eb8729d0f7abd08885f986e3bfacd5c1f205516fe79bc75a1ac94e025c80');ALT=(f'{BASE}/batch-affected-alternate.json','67da7568d7cde0389235b51b0f1a01383876dd07cc9dda223db2d1752db3f4dd');OUT=(f'{BASE}/batch-outside.json','324a57cd775bcf0e0f04a88ca9c84eeab858e91c9fcfa10568561f6dc959fd34');P=R/'.private'/('hardened-'+A.lower()+'.json');O=R/'verification'/('live-'+A.lower()+'.json')
def rpc(m,p):
 x=requests.post(RPC,json={'jsonrpc':'2.0','id':1,'method':m,'params':p},timeout=45);x.raise_for_status();d=x.json()
 if 'error'in d:raise RuntimeError(d['error'])
 return d['result']
def view(m,args=[]):
 d=serialize([calldata.encode({'method':m,'args':args}),b'\0']);r=rpc('gen_call',[{'type':'read','to':A,'from':'0x0000000000000000000000000000000000000001','value':'0x0','data':d,'transaction_hash_variant':'latest-final'}]);return str(calldata.decode(bytes.fromhex(r.removeprefix('0x'))))
def ret(t):
 rs=t['consensus_data']['leader_receipt'];rs=[rs]if isinstance(rs,dict)else rs;r=[x for x in rs if x.get('mode')=='leader'][-1];v=r['result'];z=base64.b64decode(v['raw']if isinstance(v,dict)else v)
 if r['execution_result']!='SUCCESS'or z[0]!=0:raise RuntimeError('EXECUTION_FAILED')
 return str(calldata.decode(z[1:]))
def save(j):
 P.parent.mkdir(exist_ok=True);P.write_text(json.dumps(j,indent=2));q=json.loads(json.dumps(j));[x.pop('receipt',None)for x in q['steps']];O.write_text(json.dumps(q,indent=2)+'\n')
def snapshot():
 counts=view('get_counts');r={'counts':counts}
 for i in range(int(counts.split('|')[0])):r[f'recall{i}']=view('get_recall',[i])
 for i in range(int(counts.split('|')[1])):r[f'screen{i}']=view('get_screen',[i])
 return r
def main():
 if not sys.stdin.isatty():raise RuntimeError('TTY_REQUIRED')
 keys=json.loads(getpass.getpass('TWO_TEST_KEYS_NO_ECHO: '));accounts=[create_account(account_private_key='0x'+x.removeprefix('0x'))for x in keys];del keys
 if len(accounts)!=2:raise RuntimeError('TWO_KEYS_REQUIRED')
 if hashlib.sha256((R/'contracts'/'RecallBatchBoundaryRegistry.py').read_bytes()).hexdigest()!=SH or base64.b64decode(rpc('gen_getContractCode',[A]))!=(R/'contracts'/'RecallBatchBoundaryRegistry.py').read_bytes():raise RuntimeError('SOURCE_MISMATCH')
 clients={x.address.lower():create_client(chain=studionet,account=x)for x in accounts};owner,attestor=accounts
 plan=[('F1-untrusted-publish',attestor,'register_recall',[RC[0],RC[1]],'PUBLISHER_ONLY'),('F2-untrusted-screen',attestor,'screen_batch',[0,IN[0],IN[1]],'ATTESTOR_ONLY'),('F3-nonowner-grant',owner,'set_attestor',[attestor.address,True],'OWNER_ONLY'),('F4-nonowner-setpublisher',attestor,'set_publisher',[attestor.address,True],'OWNER_ONLY'),('H1-register',owner,'register_recall',[RC[0],RC[1]],'0'),('F5-wrong-publisher-activate',attestor,'activate_recall',[0],'PUBLISHER_ONLY'),('H2-activate',owner,'activate_recall',[0],'RECALL_ACTIVATED'),('H3-affected',attestor,'screen_batch',[0,IN[0],IN[1]],'0'),('H4-outside',attestor,'screen_batch',[0,OUT[0],OUT[1]],'1'),('A1-canonical-duplicate',attestor,'screen_batch',[0,ALT[0],ALT[1]],'DUPLICATE_SCREEN'),('H5-register-replacement',owner,'register_recall',[RC[0],RC[1]],'1'),('H6-activate-replacement',owner,'activate_recall',[1],'RECALL_ACTIVATED'),('H7-supersede',owner,'supersede_recall',[0,1],'RECALL_SUPERSEDED'),('F6-old-campaign-screen',attestor,'screen_batch',[0,OUT[0],OUT[1]],'RECALL_NOT_ACTIVE')]
 j=json.loads(P.read_text())if P.exists()else{'contract':A,'source_sha256':SH,'fixture_commit':C,'wallets':[x.address for x in accounts],'steps':[],'complete':False}
 j['fixture_commit']=C
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
    item.update({'actual':got,'readback':snapshot(),'receipt':tx,'status':'VERIFIED'});save(j);print(json.dumps({'step':name,'actual':got,'readback':item['readback']}),flush=True);break
   time.sleep(8)
  else:raise RuntimeError('POLL_TIMEOUT_KEEP_HASH')
 j['complete']=True;save(j);print(json.dumps({'complete':True,'steps':len(plan)}))
if __name__=='__main__':main()
