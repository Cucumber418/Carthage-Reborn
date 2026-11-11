"""Load explicit dynamic-name entry modes and exercise independent naming."""
from pathlib import Path
import unittest

from test_territories import Node, World, entries, get, load_scripts
from test_localization import load_localization
from territory_test_data import EUROPE

ROOT = Path(__file__).resolve().parents[1]
PATCH = 'common/dynamic_country_names/zz_crb_independent_names.txt'
OLD_NAMES = {
    'TRP': ('的黎波里', 'Tripolitania'),
    'NUM': ('努米底亚', 'Numidia'),
    'IBT': ('伊比利亚', 'Iberia'),
    'GLT': ('高卢', 'Gaul'),
    'SNT': ('阿尔卑斯', 'Alps'),
    'IOP': ('伊奥尼亚', 'Ionia'),
    'RPR': ('罗马', 'Rome'),
    'CPM': ('毛里塔尼亚', 'Mauretania'),
    'CPE': ('埃及', 'Egypt'),
    'CPF': ('腓尼基', 'Phoenicia'),
    'CPS': ('叙利亚', 'Syria'),
    'CPB': ('美索不达米亚', 'Mesopotamia'),
    'CPA': ('阿拉伯', 'Arabia'),
}
EXPECTED = OLD_NAMES | {r['tag']: (r['name_zh'], r['name_en']) for r in EUROPE}


def dynamic_database(scripts, include_patch=True):
    """Apply object-level entry modes without implicitly overwriting bare keys."""
    database = {}
    for path, nodes in sorted(scripts.items()):
        if not path.startswith('common/dynamic_country_names/'):
            continue
        if path == PATCH and not include_patch:
            continue
        for node in nodes:
            if not isinstance(node, Node):
                continue
            mode, separator, tag = node.key.partition(':')
            if not separator:
                tag = mode
                if tag in database:
                    raise AssertionError('Implicit replacement is not supported: ' + tag)
                database[tag] = list(node.value)
            elif mode == 'REPLACE':
                database[tag] = list(node.value)
            elif mode == 'INJECT_OR_CREATE':
                database.setdefault(tag, []).extend(node.value)
            else:
                raise AssertionError('Unsupported entry mode: ' + mode)
    return database


def selected_name(database, tag, world):
    candidates = [node.value for node in entries(database.get(tag, []), 'dynamic_country_name')
                  if world.conditions(get(node.value, 'trigger', []), world.ctx())]
    if not candidates:
        return tag
    # max retains the first definition on equal priorities, matching the schema.
    selected = max(candidates, key=lambda nodes: int(get(nodes, 'priority', '0')))
    return get(selected, 'name', tag)


class IndependentNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()
        cls.before = dynamic_database(cls.scripts, include_patch=False)
        cls.after = dynamic_database(cls.scripts)
        cls.locales = {language: load_localization(language)
                       for language in ('simp_chinese', 'english')}

    def test_all_subject_tags_use_supported_explicit_entry_modes_and_geographic_names(self):
        self.assertEqual(len(EXPECTED), 25)
        self.assertTrue((ROOT / PATCH).read_bytes().startswith(b'\xef\xbb\xbf'))
        patch = self.scripts[PATCH]
        self.assertEqual({node.key for node in patch},
                         {'INJECT_OR_CREATE:' + tag for tag in EXPECTED})
        for node in patch:
            tag = node.key.split(':', 1)[1]
            with self.subTest(tag=tag):
                definitions = entries(node.value, 'dynamic_country_name')
                self.assertEqual(len(definitions), 1)
                definition = definitions[0].value
                self.assertEqual(get(definition, 'name'), tag + '_crb_independent')
                self.assertEqual(get(definition, 'adjective'), tag + '_ADJ')
                self.assertEqual(get(definition, 'is_main_tag_only'), 'yes')
                self.assertEqual(int(get(definition, 'priority')), 1000)
                key = get(definition, 'name')
                self.assertEqual(self.locales['simp_chinese'][key], EXPECTED[tag][0])
                self.assertEqual(self.locales['english'][key], EXPECTED[tag][1])

    def test_injection_preserves_subject_rules_and_creates_missing_ionian_and_roman_objects(self):
        self.assertNotIn('IOP', self.before)
        self.assertNotIn('RPR', self.before)
        self.assertEqual(set(self.after), set(self.before) | {'IOP', 'RPR'})
        for tag in EXPECTED:
            with self.subTest(tag=tag):
                self.assertEqual(self.after[tag][:-1], self.before.get(tag, []))
                self.assertEqual(self.after[tag][-1].key, 'dynamic_country_name')
        self.assertEqual(self.after['TUN'], self.before['TUN'])

    def test_names_follow_independence_without_changing_attached_foreign_or_unmarked_countries(self):
        for tag in EXPECTED:
            for province in (False, True):
                for state in ('attached', 'independent', 'foreign_subject', 'unmarked'):
                    with self.subTest(tag=tag, province=province, state=state):
                        world = World(self.scripts)
                        world.country('FRA')
                        flags = {'crb_carthaginian_subject'} | ({'crb_province'} if province else set())
                        if state == 'unmarked':
                            flags.discard('crb_carthaginian_subject')
                        overlord = 'TUN' if state == 'attached' else 'FRA' if state == 'foreign_subject' else ''
                        subject = world.country(tag, overlord=overlord, variables=flags,
                                                laws={'law_type:law_parliamentary_republic'})
                        world.saved['actor'] = subject
                        before_flags, before_laws = set(subject.variables), set(subject.laws)
                        expected = (tag + '_crb_independent' if state == 'independent'
                                    else selected_name(self.before, tag, world))
                        self.assertEqual(selected_name(self.after, tag, world), expected)
                        self.assertEqual(subject.variables, before_flags)
                        self.assertEqual(subject.laws, before_laws)
                        world.saved.pop('actor')
                        self.assertEqual(selected_name(self.after, tag, world), tag)
