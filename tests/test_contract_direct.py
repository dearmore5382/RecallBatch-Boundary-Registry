import hashlib,json
from pathlib import Path
from unittest.mock import patch
from gltest.direct import VMContext,create_address,deploy_contract
ROOT=Path(__file__).resolve().parents[1];CONTRACT=ROOT/'contracts'/'RecallBatchBoundaryRegistry.py'
R=json.dumps({'schema_version':'1.0','recall_ref':'RC-24','manufacturer':'AquaPure','product_code':'X2','regions':['EU'],'lot_prefix':'APX2-','lot_start':240100,'lot_end':240899,'qualifier':''},separators=(',',':'))
def batch(issuer,ref='B-412',lot='APX2-240412'):return json.dumps({'schema_version':'1.0','batch_ref':ref,'issuer':str(issuer),'manufacturer':'AquaPure','product_code':'X2','region':'EU','lot_code':lot,'attributes':{}},separators=(',',':'))
def sha(v):return hashlib.sha256(v.encode()).hexdigest()
def eth(v):
 if isinstance(v,bytes):return '0x'+bytes(v).hex()
 s=str(v);return '0x'+s[5:] if s.startswith('addr#') else s
def deploy():
 owner,attacker,attestor=create_address('owner'),create_address('attacker'),create_address('attestor');vm=VMContext(owner)
 with patch('os.unlink',lambda _:None),vm.activate():c=deploy_contract(CONTRACT,vm);gl=c._instance.register_recall.__globals__['gl'];_=gl.nondet
 return vm,c,owner,attacker,attestor
def sync(vm,c):
 gl=c._instance.register_recall.__globals__['gl'];sender=vm.sender
 if isinstance(sender,bytes):sender=type(gl.message.sender_address)(sender)
 gl._cached_gl.message=gl.message._replace(sender_address=sender,origin_address=sender,value=type(gl.message.value)(vm.value))
def activate(vm,c):
 with vm.activate():sync(vm,c);rid=c.register_recall('https://x/r',sha(R))
 with vm.activate(),patch.dict(c._instance.register_recall.__globals__,{'_fetch':lambda _:R}):sync(vm,c);assert c.activate_recall(rid)=='RECALL_ACTIVATED'
 return rid
def test_untrusted_accounts_cannot_publish_or_attest():
 vm,c,_,attacker,_=deploy()
 with vm.prank(attacker):sync(vm,c);assert c.register_recall('https://x/r',sha(R))=='PUBLISHER_ONLY';assert c.screen_batch(0,'https://x/b','0'*64)=='ATTESTOR_ONLY'
 assert c.get_counts()=='0|0'
def test_owner_manages_roles_and_only_publisher_activates():
 vm,c,owner,attacker,_=deploy()
 with vm.activate():sync(vm,c);assert c.set_publisher(eth(attacker),True)=='PUBLISHER_UPDATED'
 with vm.prank(attacker):sync(vm,c);rid=c.register_recall('https://x/r',sha(R))
 with vm.activate():sync(vm,c);assert c.activate_recall(rid)=='PUBLISHER_ONLY';assert c.set_attestor(eth(attacker),True)=='ATTESTOR_UPDATED';assert c.get_role(eth(owner)).startswith('OWNER|True|True')
 with vm.activate():sync(vm,c);c.set_publisher(eth(attacker),False)
 with vm.prank(attacker):sync(vm,c);assert c.activate_recall(rid)=='PUBLISHER_ONLY'
def test_many_batches_and_canonical_duplicate():
 vm,c,_,_,attestor=deploy();rid=activate(vm,c)
 with vm.activate():sync(vm,c);c.set_attestor(eth(attestor),True)
 b1=batch(eth(attestor));b2=batch(eth(attestor),'B-950','APX2-240950');module=c._instance.register_recall.__globals__
 with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:b1}):sync(vm,c);s0=c.screen_batch(rid,'https://x/b1',sha(b1));assert c.get_screen(s0).split('|')[-2]=='AFFECTED'
 with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:b2}):sync(vm,c);s1=c.screen_batch(rid,'https://x/b2',sha(b2));assert c.get_screen(s1).split('|')[-2]=='NOT_AFFECTED'
 changed=json.dumps(json.loads(b1),indent=2)
 with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:changed}):sync(vm,c);assert c.screen_batch(rid,'https://x/changed',sha(changed))=='DUPLICATE_SCREEN'
 changed_ref=json.loads(b1);changed_ref['batch_ref']='OTHER-REFERENCE';changed_ref=json.dumps(changed_ref,separators=(',',':'))
 with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:changed_ref}):sync(vm,c);assert c.screen_batch(rid,'https://x/ref',sha(changed_ref))=='DUPLICATE_SCREEN'
 assert c.get_counts()=='1|2'
def test_issuer_mismatch_is_atomic():
 vm,c,_,_,attestor=deploy();rid=activate(vm,c)
 with vm.activate():sync(vm,c);c.set_attestor(eth(attestor),True)
 forged=batch(eth(create_address('victim')));module=c._instance.register_recall.__globals__
 with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:forged}):sync(vm,c);assert c.screen_batch(rid,'https://x/b',sha(forged))=='ISSUER_MISMATCH'
 assert c.get_counts()=='1|0'
def test_suspend_and_supersede():
 vm,c,_,_,_=deploy();old=activate(vm,c)
 with vm.activate():sync(vm,c);assert c.suspend_recall(old)=='RECALL_SUSPENDED';new=c.register_recall('https://x/new',sha(R))
 with vm.activate(),patch.dict(c._instance.register_recall.__globals__,{'_fetch':lambda _:R}):sync(vm,c);c.activate_recall(new);assert c.supersede_recall(old,new)=='RECALL_SUPERSEDED';assert c.get_recall(old).split('|')[-1]=='1'
def test_ai_never_creates_not_affected_from_qualifier():
 q=json.loads(R);q['qualifier']='retail only';r=json.dumps(q,separators=(',',':'))
 for token in ('NO_MATCH','UNCLEAR'):
  vm,c,_,_,attestor=deploy();module=c._instance.register_recall.__globals__
  with vm.activate():sync(vm,c);rid=c.register_recall('https://x/r',sha(r));c.set_attestor(eth(attestor),True)
  with vm.activate(),patch.dict(module,{'_fetch':lambda _:r}):sync(vm,c);c.activate_recall(rid)
  b=batch(eth(attestor),token)
  with vm.prank(attestor),patch.dict(module,{'_fetch':lambda _:b,'_qualifier':lambda *_:token}):sync(vm,c);sid=c.screen_batch(rid,'https://x/'+token,sha(b));assert c.get_screen(sid).split('|')[-2]=='MANUAL_REVIEW'
