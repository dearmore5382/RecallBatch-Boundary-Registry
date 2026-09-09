"""Read-only deployed-source parity gate."""
import base64,hashlib,json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1];RPC='https://studio.genlayer.com/api';ADDRESS='0xE36aE6FF03dFf98c81DA20d19A058e1c991960fc'
def rpc(method,params):
 r=requests.post(RPC,json={'jsonrpc':'2.0','id':1,'method':method,'params':params},timeout=45);r.raise_for_status();d=r.json()
 if 'error'in d:raise RuntimeError(d['error'])
 return d['result']
def main():
 local=(ROOT/'contracts'/'RecallBatchBoundaryRegistry.py').read_bytes();deployed=base64.b64decode(rpc('gen_getContractCode',[ADDRESS]));result={'contract':ADDRESS,'chain_id':int(rpc('eth_chainId',[]),16),'local_sha256':hashlib.sha256(local).hexdigest(),'deployed_sha256':hashlib.sha256(deployed).hexdigest(),'exact_source_parity':local==deployed};(ROOT/'verification'/('preflight-'+ADDRESS.lower()+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['exact_source_parity'],'SOURCE_MISMATCH'
if __name__=='__main__':main()
