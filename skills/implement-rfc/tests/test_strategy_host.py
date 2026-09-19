"""Scoped controls and contamination observations without native sessions."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import tomllib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import execution_strategy as strategy
import strategy_host as host


class HostTests(unittest.TestCase):
    def test_direct_native_controls_and_zero_child_is_not_an_error(self):
        direct=strategy.resolve('direct-astra-max');native=strategy.resolve('native-astra-ultra')
        self.assertFalse(tomllib.loads(host.render(direct))['agents']['enabled'])
        rendered=tomllib.loads(host.render(native))
        self.assertEqual(rendered['model_reasoning_effort'],'ultra')
        self.assertEqual(rendered['agents'],{'enabled':True})
        self.assertEqual(native['instruction_paths'],['references/engineering-contract.md','references/strategies/native.md'])
        self.assertEqual(native['owners']['engineering'],'primary')
        with tempfile.TemporaryDirectory() as directory:
            config=Path(directory)/'config.toml';config.write_text(host.render(native));before=config.read_bytes()
            result=host.inspect(native,[config],complete_inputs=True)
            self.assertEqual(result['state'],'configuration_consistent')
            self.assertEqual(result['host_load'],'not_verified')
            self.assertEqual(config.read_bytes(),before)
            self.assertEqual(host.inspect(native,[config])['state'],'incomplete')

    def test_inherited_roles_routes_and_directive_signals(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);inherited=root/'global.toml';scoped=root/'scoped.toml';instructions=root/'AGENTS.md';agents=root/'agents';agents.mkdir()
            inherited.write_text('[agents]\ndefault_subagent_model="custom"\ndefault_subagent_reasoning_effort="low"\n')
            selected=strategy.resolve('native-astra-ultra');scoped.write_text(host.render(selected))
            instructions.write_text('You are the coordinator. Dispatch an rfc-integrator.\n')
            (agents/'rfc-worker.toml').write_text('name="rfc-worker"\n')
            result=host.inspect(selected,[inherited,scoped],[instructions],[agents],complete_inputs=True)
            kinds={item['kind'] for item in result['findings']}
            self.assertTrue({'inherited_child_route_override','possible_custom_coordination_instruction','custom_agent_definition'}<=kinds)
            self.assertEqual(result['state'],'needs_reconciliation')
            self.assertEqual(inherited.read_text(),'[agents]\ndefault_subagent_model="custom"\ndefault_subagent_reasoning_effort="low"\n')
            result=host.inspect(strategy.resolve('direct-astra-max'),[scoped])
            self.assertIn('delegation_control_mismatch',[item['kind'] for item in result['findings']])
