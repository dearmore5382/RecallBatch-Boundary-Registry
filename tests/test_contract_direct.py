import hashlib,json
from pathlib import Path
from unittest.mock import patch
from gltest.direct import VMContext,create_address,deploy_contract
ROOT=Path(__file__).resolve().parents[1];CONTRACT=ROOT/'contracts'/'RecallBatchBoundaryRegistry.py'
R=json.dumps({'schema_version':'1.0','recall_ref':'RC-24','manufacturer':'AquaPure','product_code':'X2','regions':['EU'],'lot_prefix':'APX2-','lot_start':240100,'lot_end':240899,'qualifier':''},separators=(',',':'))
def batch(ref='B-412',lot='APX2-240412',region='EU'):return json.dumps({'schema_version':'1.0','batch_ref':ref,'manufacturer':'AquaPure','product_code':'X2','region':region,'lot_code':lot,'attributes':{}},separators=(',',':'))
def sha(v):return hashlib.sha256(v.encode()).hexdigest()
def deploy():
 owner,other=create_address('owner'),create_address('other');vm=VMContext(owner)
 with patch('os.unlink',lambda _:None),vm.activate():c=deploy_contract(CONTRACT,vm);gl=c._instance.register_recall.__globals__['gl'];_=gl.nondet
 return vm,c,owner,other
def sync(vm,c):
 gl=c._instance.register_recall.__globals__['gl'];sender=vm.sender
 if isinstance(sender,bytes):sender=type(gl.message.sender_address)(sender)
 gl._cached_gl.message=gl.message._replace(sender_address=sender,origin_address=sender,value=type(gl.message.value)(vm.value))
def activate(vm,c):
 with vm.activate():sync(vm,c);rid=c.register_recall('https://x/recall.json',sha(R))
 module=c._instance.register_recall.__globals__
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:R}):sync(vm,c);assert c.activate_recall(rid)=='RECALL_ACTIVATED'
 return rid
def screen(vm,c,rid,b):
 module=c._instance.register_recall.__globals__
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:b}):sync(vm,c);return c.screen_batch(rid,'https://x/batch.json',sha(b))
def test_campaign_activation_authority_and_atomic_hash_failure():
 vm,c,_,other=deploy()
 with vm.activate():sync(vm,c);rid=c.register_recall('https://x/recall.json',sha(R))
 with vm.prank(other):sync(vm,c);assert c.activate_recall(rid)=='CREATOR_ONLY'
 module=c._instance.register_recall.__globals__
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:R+' '}):sync(vm,c);assert c.activate_recall(rid)=='RECALL_HASH_MISMATCH'
 assert c.get_recall(rid).split('|')[0]=='REGISTERED'
def test_one_campaign_screens_many_batches():
 vm,c,_,_=deploy();rid=activate(vm,c);inside=batch();outside=batch('B-950','APX2-240950')
 a=screen(vm,c,rid,inside);b=screen(vm,c,rid,outside)
 assert c.get_screen(a).split('|')[-2]=='AFFECTED';assert c.get_screen(b).split('|')[-2]=='NOT_AFFECTED';assert c.get_counts()=='1|2'
def test_duplicate_digest_rejected_without_new_record():
 vm,c,_,_=deploy();rid=activate(vm,c);b=batch();assert screen(vm,c,rid,b)==0;assert screen(vm,c,rid,b)=='DUPLICATE_SCREEN';assert c.get_counts()=='1|1'
def test_structured_path_never_calls_ai():
 vm,c,_,_=deploy();rid=activate(vm,c);module=c._instance.register_recall.__globals__;b=batch()
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:b,'_qualifier':lambda *_:(_ for _ in()).throw(AssertionError())}):sync(vm,c);sid=c.screen_batch(rid,'https://x/batch.json',sha(b));assert sid==0
def test_qualifier_can_fail_closed_to_manual_review():
 q=json.loads(R);q['qualifier']='retail only';r=json.dumps(q,separators=(',',':'));b=batch();vm,c,_,_=deploy()
 with vm.activate():sync(vm,c);rid=c.register_recall('https://x/r.json',sha(r))
 module=c._instance.register_recall.__globals__
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:r}):sync(vm,c);c.activate_recall(rid)
 with vm.activate(),patch.dict(module,{'_fetch':lambda _:b,'_qualifier':lambda *_:'UNCLEAR'}):sync(vm,c);sid=c.screen_batch(rid,'https://x/b.json',sha(b));assert c.get_screen(sid).split('|')[-2]=='MANUAL_REVIEW'
