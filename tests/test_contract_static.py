import ast
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'contracts'/'RecallBatchBoundaryRegistry.py';S=P.read_text();T=ast.parse(S)
def test_contract_shape():
 names={n.name for n in ast.walk(T) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))};assert {'register_recall','activate_recall','screen_batch','get_recall','get_screen','get_counts'}<=names
def test_security_invariants():
 assert 'strict_eq' in S and 'comparative' not in S and '@gl.public.payable' not in S and 'sha256' in S and 'CREATOR_ONLY' in S
def test_ai_is_narrow_and_optional():
 assert 'MATCH, NO_MATCH, or UNCLEAR' in S and "not r['qualifier'].strip()" in S and 'WITHIN_STRUCTURED_BOUNDARY' in S
