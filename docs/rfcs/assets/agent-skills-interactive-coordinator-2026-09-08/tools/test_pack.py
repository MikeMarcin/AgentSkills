#!/usr/bin/env python3
"""Mutation checks for the RFC packet validator, not a model benchmark."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import validate_pack as checker

ROOT=Path(__file__).resolve().parents[1]

class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='agentskills-packet-check-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'packet'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    def edit(self,rel,fn):
        p=self.root/rel;p.write_text(fn(p.read_text()),encoding='utf-8')
    def json_edit(self,rel,fn):
        p=self.root/rel;v=json.loads(p.read_text());fn(v);p.write_text(json.dumps(v),encoding='utf-8')
    def has(self,word,manifest=False):
        findings=checker.validate(self.root,check_manifest=manifest)
        self.assertTrue(any(word in x for x in findings),findings)
    def test_valid_packet(self):
        self.assertEqual(checker.validate(self.root),[])
    def test_integrity_change(self):
        self.edit('README.md',lambda x:x+'\nChanged.\n');self.has('content mismatch',True)
    def test_missing_member(self):
        (self.root/'ROUTING.md').unlink();self.has('absent member',True)
    def test_unexpected_file(self):
        (self.root/'unlisted.txt').write_text('extra');self.has('member set',True)
    def test_manifest_traversal(self):
        self.json_edit('PACK_MANIFEST.json',lambda x:x['files'].append({'path':'../outside','bytes':0,'sha256':'0'*64}));self.has('unsafe',True)
    def test_missing_criterion(self):
        p=next((self.root/'docs/rfcs').glob('RFC-*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('**RFC-ASK-0010-AC14 —','**Removed —'));self.has('fourteen')
    def test_dangling_dependency(self):
        p=next((self.root/'docs/issues/10-backlog').glob('ASK-0051*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('depends_on: ["ASK-0050"]','depends_on: ["ASK-9999"]'));self.has('dependency target')
    def test_dependency_cycle(self):
        p=next((self.root/'docs/issues/20-ready').glob('ASK-0050*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('depends_on: []','depends_on: ["ASK-0051"]'));self.has('dependency cycle')
    def test_wrong_ready_status(self):
        p=next((self.root/'docs/issues/10-backlog').glob('ASK-0051*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('status: "Backlog"','status: "Ready"'));self.has('status/lane')
    def test_missing_closeout(self):
        p=next((self.root/'docs/issues/10-backlog').glob('ASK-0058*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('closeout_for: ["RFC-ASK-0010"]','closeout_for: []'));self.has('exactly ASK-0058')
    def test_fabricated_baseline(self):
        p=next((self.root/'docs/issues/10-backlog').glob('ASK-0058*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('RFC_BASE_SHA: UNRECORDED','RFC_BASE_SHA: '+'a'*40));self.has('fabricated packet baseline')
    def test_coordinator_effort_drift(self):
        self.json_edit('fixtures/target-routing.json',lambda x:x['coordinator']['codex'].update(effort='medium'));self.has('coordinator pair')
    def test_leaf_route_drift(self):
        self.json_edit('fixtures/target-routing.json',lambda x:x['preserved_routing_snapshot']['providers']['codex']['classes']['review'].update(effort='low'));self.has('leaf routes changed')
    def test_topology_drift(self):
        self.json_edit('fixtures/target-routing.json',lambda x:x['ordinary_topology'].update(leaf_children=['rfc-integrator']));self.has('ordinary topology')
    def test_nonportable_frontmatter(self):
        self.edit('draft/skills/implement-rfc/SKILL.md',lambda x:x.replace('name: implement-rfc','name: implement-rfc\ndisable-model-invocation: true'));self.has('nonportable')
    def test_broken_link(self):
        self.edit('README.md',lambda x:x+'\n[missing](does-not-exist.md)\n');self.has('links: missing')
    def test_duplicate_case(self):
        self.json_edit('fixtures/coordination-cases.json',lambda x:x['cases'].append(copy.deepcopy(x['cases'][0])));self.has('duplicate')
    def test_false_pack_complete(self):
        self.json_edit('fixtures/return.example.json',lambda x:x.update(disposition='pack-complete'));self.has('pack completion prerequisites')
    def test_usage_doublecount_expected(self):
        self.json_edit('fixtures/owning-response.synthetic.json',lambda x:x['expected'].update(input_tokens=1050));self.has('hand-calculated totals')
    def test_return_valid_completion_structural_only(self):
        v=json.loads((self.root/'fixtures/return.example.json').read_text())
        v.update(disposition='pack-complete',ownership='quiescent',next_objective=None,required_pending=[],evidence_refs=['synthetic-fixture-only'])
        self.assertEqual(checker.return_findings(v),[])
    def test_case_collision(self):
        if (self.root/'readme.md').exists():
            self.skipTest('case collision requires a case-sensitive fixture filesystem')
        (self.root/'readme.md').write_text('collision');self.has('case collision')
    def test_implementation_coverage_missing(self):
        self.json_edit('issue-plan.json',lambda x:[r['acs'].remove('AC10') for r in x['cards'] if r['id']!='ASK-0058' and 'AC10' in r['acs']]);self.has('acceptance coverage')
    def test_premature_acceptance(self):
        p=next((self.root/'docs/issues/10-backlog').glob('ASK-0058*.md'))
        self.edit(p.relative_to(self.root),lambda x:x.replace('| Not run | Unrecorded |','| PASS | fabricated |',1));self.has('premature packet acceptance')
    def test_duplicate_json_key(self):
        self.edit('fixtures/return.example.json',lambda x:x.replace('"schema":', '"schema": "duplicate", "schema":',1));self.has('duplicate JSON key')

if __name__=='__main__':unittest.main(verbosity=2)
