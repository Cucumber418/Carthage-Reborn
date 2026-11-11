"""The pinned native independence events differ only by our duplicate-menu guard."""
import copy
import hashlib
import json
import unittest

from territory_test_data import NATIVE_EVENT_COMPAT
from test_territories import GOVERNANCE_LAWS, Node, World, entries, get, load_scripts


def canonical(value):
    if isinstance(value, Node):
        return [value.key, value.op, canonical(value.value)]
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


class NativeIndependenceCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()

    def test_whole_native_file_matches_pinned_source_after_removing_only_duplicate_menu_guard(self):
        nodes = copy.deepcopy(self.scripts[NATIVE_EVENT_COMPAT['path']])
        events = {node.key: node.value for node in nodes if isinstance(node, Node)
                  and node.key != 'namespace'}
        self.assertEqual(set(events), set(NATIVE_EVENT_COMPAT['events']))
        all_keys = set()
        for key, event in events.items():
            keys = {get(event, part) for part in ('title', 'desc', 'flavor')}
            keys.update(get(option.value, 'name') for option in entries(event, 'option'))
            self.assertEqual(keys, set(NATIVE_EVENT_COMPAT['events'][key]))
            all_keys.update(keys)
        self.assertEqual(all_keys, set(NATIVE_EVENT_COMPAT['localization_keys']))
        cancellation = entries(events['independence.2'], 'cancellation_trigger')
        self.assertEqual(len(cancellation), 1)
        self.assertEqual(cancellation[0].value, [Node('OR', '=', [
            Node('is_subject', '=', 'yes'),
            Node('has_variable', '=', 'crb_carthaginian_subject'),
        ])])
        cancellation[0].value = [Node('is_subject', '=', 'yes')]
        raw = json.dumps(canonical(nodes), ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.assertEqual(hashlib.sha256(raw).hexdigest(), NATIVE_EVENT_COMPAT['canonical_sha256'])

    def test_only_marked_or_still_subject_countries_cancel_the_native_menu(self):
        for marked in (False, True):
            for subject in (False, True):
                for law in sorted(GOVERNANCE_LAWS):
                    with self.subTest(marked=marked, subject=subject, law=law):
                        world = World(self.scripts)
                        country = world.country('NUM',
                            variables={'crb_carthaginian_subject'} if marked else set(),
                            overlord='TUN' if subject else '', laws={law})
                        native = world.defs['independence.2']
                        self.assertEqual(world.conditions(get(native, 'cancellation_trigger'),
                                                          world.ctx(country.tag)), marked or subject)
                        # Simulate the original Colonial Administration hook's day-one request.
                        world.effect([Node('trigger_event', '=', [
                            Node('id', '=', 'independence.2'), Node('days', '=', '1'),
                        ])], world.ctx(country.tag))
                        world.fire_scheduled_day_events()
                        self.assertEqual(world.events, [] if marked or subject else ['independence.2'])
                        self.assertEqual(country.laws, {law})
                        if not marked and not subject:
                            default = next(option.value for option in entries(native, 'option')
                                           if get(option.value, 'default_option') == 'yes')
                            world.effect([node for node in default if node.key not in
                                          ('name', 'default_option')], world.ctx(country.tag))
                            self.assertEqual(country.laws, {'law_type:law_parliamentary_republic'})
                        # The other native event retains its original subject-only cancellation.
                        self.assertEqual(world.conditions(
                            get(world.defs['independence.1'], 'cancellation_trigger'),
                            world.ctx(country.tag)), subject)
        self.assertIsNone(get(World(self.scripts).defs['crb_independence.1'], 'after'))


if __name__ == '__main__':
    unittest.main()
