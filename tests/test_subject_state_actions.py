"""Verify the state-transfer compatibility patch preserves vanilla 1.15 rules."""
import hashlib
import json
from pathlib import Path
import unittest

from test_territories import Node, parse

ROOT = Path(__file__).resolve().parents[1]
CUSTOM_TYPES = {'subject_type_crb_trading_post', 'subject_type_crb_province'}
VANILLA_TYPES = {'subject_type_colony', 'subject_type_puppet', 'subject_type_vassal'}


def canonical(value):
    if isinstance(value, Node):
        return [value.key, value.op, canonical(value.value)]
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


class SubjectStateActionTests(unittest.TestCase):
    def test_only_subject_type_whitelists_differ_from_vanilla_1_15(self):
        fixture = json.loads((ROOT / 'tests/fixtures/vanilla_subject_state_actions_1_15.json').read_text())
        path = ROOT / 'common/diplomatic_actions/zz_crb_subject_state_transfers.txt'
        self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'))
        actions = parse(path.read_text(encoding='utf-8-sig'))
        self.assertEqual({action.key for action in actions}, set(fixture['canonical_sha256']))

        for action in actions:
            with self.subTest(action=action.key):
                additions = []

                def without_custom_types(value, parent_key=None):
                    if isinstance(value, Node):
                        return Node(value.key, value.op, without_custom_types(value.value, value.key))
                    if not isinstance(value, list):
                        return value
                    custom = [node for node in value if isinstance(node, Node)
                              and node.key == 'is_subject_type' and node.value in CUSTOM_TYPES]
                    if custom:
                        self.assertEqual(parent_key, 'OR')
                        self.assertEqual(len(value), len(VANILLA_TYPES | CUSTOM_TYPES))
                        self.assertEqual({node.value for node in value}, VANILLA_TYPES | CUSTOM_TYPES)
                        self.assertTrue(all(node.key == 'is_subject_type' and node.op == '=' for node in value))
                        additions.append(custom)
                    return [without_custom_types(node) for node in value if node not in custom]

                normalized = without_custom_types(action)
                self.assertEqual(len(additions), fixture['extended_whitelist_counts'][action.key])
                payload = json.dumps(canonical(normalized), ensure_ascii=False, separators=(',', ':')).encode()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), fixture['canonical_sha256'][action.key],
                                 'Vanilla selection rules, effects or AI changed beyond the subject-type additions')
