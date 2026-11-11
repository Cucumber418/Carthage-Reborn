"""European territorial lifecycle scenarios against the actual mod scripts."""
from collections import Counter
import json
import unittest

from test_territories import ECONOMIC_LAWS, Fleet, Node, World, entries, get, load_scripts, subst
from test_localization import load_localization
from territory_test_data import EUROPE, TOTAL_REGIONS, buttons, formation_buttons

COOLDOWN = 'crb_territory_disposition_cooldown'
JOURNAL = 'je_crb_territories'


def payload(option):
    return [node for node in option if node.key not in
            ('name', 'trigger', 'default_option', 'show_as_unavailable', 'ai_chance')]


class EuropeTerritoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()
        cls.locales = {lang: load_localization(lang) for lang in ('simp_chinese', 'english')}

    def world(self, region, state=None, colonial_policy='law_type:law_no_colonial_affairs'):
        world = World(self.scripts)
        world.countries['TUN'].laws = {colonial_policy, 'law_type:law_interventionism'}
        world.country('FRA')
        land = world.land(state or region['capital'])
        return world, land

    def option(self, world, region, suffix):
        return next(node.value for node in entries(world.defs[region['event']], 'option')
                    if get(node.value, 'name') == region['event'] + '.' + suffix)

    def found(self, world, region, province=False):
        option = self.option(world, region, 'b' if province else 'a')
        self.assertTrue(world.conditions(get(option, 'trigger'), world.ctx()))
        world.effect(payload(option), world.ctx())
        return world.countries[region['tag']]

    def test_manifest_and_actual_state_triggers_are_disjoint_from_every_existing_region(self):
        self.assertEqual(len(EUROPE), 12)
        self.assertEqual(len({r['key'] for r in EUROPE}), 12)
        self.assertEqual(len({r['tag'] for r in EUROPE}), 12)
        self.assertEqual(len({r['event'] for r in EUROPE}), 12)
        states = [state for r in EUROPE for state in r['regions']]
        self.assertTrue(states)
        self.assertEqual(len(states), len(set(states)), 'A state is assigned to multiple new regions')
        old_areas = (
            'crb_is_tripoli_post_state_trigger', 'crb_is_numidia_post_state_trigger',
            'crb_is_spanish_mainland_state_trigger', 'crb_is_gaul_post_state_trigger',
            'crb_is_alpine_post_state_trigger', 'crb_is_south_italy_state_trigger',
            'crb_is_mauretania_province_state_trigger', 'crb_is_egypt_province_state_trigger',
            'crb_is_phoenicia_province_state_trigger', 'crb_is_syria_province_state_trigger',
            'crb_is_mesopotamia_province_state_trigger', 'crb_is_arabia_province_state_trigger',
        )
        for region in EUROPE:
            self.assertIn(region['capital'], region['regions'])
            for state in region['regions']:
                with self.subTest(region=region['key'], state=state):
                    world, land = self.world(region, state)
                    ctx = world.ctx().enter(land)
                    for other in EUROPE:
                        actual = world.conditions(world.defs[f"crb_is_{other['key']}_state_trigger"], ctx)
                        self.assertEqual(actual, other is region, other['key'])
                    self.assertFalse(any(world.conditions(world.defs[key], ctx) for key in old_areas))

    def test_country_metadata_uses_real_vanilla_ids_and_nonconflicting_tags(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        vanilla = json.loads((root / 'tests/fixtures/vanilla_identifiers_1_15.json').read_text())
        world = World(self.scripts)
        for region in EUROPE:
            with self.subTest(region=region['key']):
                self.assertNotIn(region['tag'], vanilla['country_tags'])
                self.assertTrue(set(region['regions']) <= set(vanilla['states']))
                self.assertTrue(set(region['cultures']) <= set(vanilla['cultures']))
                definition = world.country_definitions[region['tag']]
                self.assertEqual(get(definition, 'capital'), region['capital'])
                self.assertEqual(set(get(definition, 'cultures')), set(region['cultures']))
                self.assertEqual(get(definition, 'religion'), 'crb_tanit')

    def test_all_foundations_and_actions_are_registered_once_in_the_territorial_journal(self):
        world = World(self.scripts)
        found = formation_buttons(self.scripts)
        expand = buttons(self.scripts, 'crb_expand_')
        convert = buttons(self.scripts, 'crb_provincialize_')
        expected = [node.key for node in found + expand + convert]
        registered = [node.value for node in entries(world.defs[JOURNAL], 'scripted_button')]
        self.assertEqual(len(found), TOTAL_REGIONS)
        self.assertEqual(len(expand), TOTAL_REGIONS * 2)
        self.assertEqual(len(convert), TOTAL_REGIONS)
        self.assertEqual(Counter(registered), Counter(expected))
        self.assertTrue(all(count == 1 for count in Counter(expected).values()))
        for path, nodes in self.scripts.items():
            if not path.startswith('common/journal_entries/'):
                continue
            for node in nodes:
                if isinstance(node, Node) and node.key != JOURNAL:
                    self.assertTrue(set(expected).isdisjoint(x.value for x in entries(node.value, 'scripted_button')))

    def test_every_state_can_found_either_form_with_local_cultures_and_creation_laws(self):
        for region in EUROPE:
            for state in region['regions']:
                for province in (False, True):
                    with self.subTest(region=region['key'], state=state, province=province):
                        world, land = self.world(region, state, 'law_type:law_colonial_exploitation')
                        foreign = world.land(state, owner='FRA')
                        capital = world.land(state, capital=True)
                        unrelated = world.land('STATE_PROVENCE')
                        founder_laws = set(world.countries['TUN'].laws)
                        world.effect(world.defs['crb_try_unlock_territorial_journal_effect'], world.ctx())
                        self.assertIn(JOURNAL, world.countries['TUN'].journals)
                        subject = self.found(world, region, province)
                        self.assertEqual((land.owner, foreign.owner, capital.owner, unrelated.owner),
                                         (region['tag'], 'FRA', 'TUN', 'TUN'))
                        self.assertEqual(subject.primary_cultures, set(region['cultures']) | {'crb_punic'})
                        self.assertEqual(subject.overlord, 'TUN')
                        self.assertEqual(subject.pact, 'crb_province' if province else 'crb_trading_post')
                        self.assertEqual('crb_province' in subject.variables, province)
                        self.assertTrue({'law_type:law_crb_governor_rule', 'law_type:law_subjecthood',
                                         'law_type:law_frontier_colonization'} <= subject.laws)
                        expected_economy = 'law_type:law_agrarianism' if province else 'law_type:law_laissez_faire'
                        self.assertEqual(subject.laws & ECONOMIC_LAWS, {expected_economy})
                        self.assertEqual(world.countries['TUN'].laws, founder_laws)
                        self.assertEqual(world.countries['TUN'].infamy, region['infamy'] if province else 0)
                        self.assertEqual(world.countries['TUN'].modifier_months[COOLDOWN], 3)
                        self.assertFalse(world.conditions(get(world.defs['je_crb_hanno_barca'], 'possible'),
                                                          world.ctx(region['tag'])))
                        before = (subject, world.countries['TUN'].infamy)
                        world.effect(payload(self.option(world, region, 'b' if province else 'a')), world.ctx())
                        self.assertEqual((world.countries[region['tag']], world.countries['TUN'].infamy), before)

    def test_stale_foundation_choices_and_foreign_existing_tags_cannot_create_or_charge(self):
        for region in EUROPE:
            for reason in ('war', 'cooldown', 'capital', 'foreign_land', 'existing_tag', 'lost_land'):
                for suffix in ('a', 'b'):
                    with self.subTest(region=region['key'], reason=reason, option=suffix):
                        world, land = self.world(region)
                        world.countries['TUN'].journals.add(JOURNAL)
                        button = world.defs[f"crb_found_{region['key']}_button"]
                        self.assertTrue(world.conditions(get(button, 'possible'), world.ctx()))
                        if reason == 'war': world.countries['TUN'].war = True
                        elif reason == 'cooldown': world.countries['TUN'].modifiers.add(COOLDOWN)
                        elif reason == 'capital': land.capital = True
                        elif reason in ('foreign_land', 'lost_land'): land.owner = 'FRA'
                        elif reason == 'existing_tag': world.country(region['tag'], overlord='FRA', treasury=1000)
                        before_tags = set(world.countries)
                        before_subject = world.countries.get(region['tag'])
                        self.assertFalse(world.conditions(get(button, 'possible'), world.ctx()))
                        world.effect(get(button, 'effect'), world.ctx())
                        self.assertFalse(world.events)
                        option = self.option(world, region, suffix)
                        self.assertFalse(world.conditions(get(option, 'trigger'), world.ctx()))
                        world.effect(payload(option), world.ctx())
                        self.assertEqual(set(world.countries), before_tags)
                        self.assertIs(world.countries.get(region['tag']), before_subject)
                        self.assertEqual(world.countries['TUN'].infamy, 0)
                        self.assertEqual(land.owner, 'FRA' if reason in ('foreign_land', 'lost_land') else 'TUN')

    def test_cancel_defaults_leave_the_land_treasury_and_shared_cooldown_untouched(self):
        for region in EUROPE:
            with self.subTest(region=region['key']):
                world, land = self.world(region)
                option = self.option(world, region, 'c')
                self.assertEqual(get(option, 'default_option'), 'yes')
                world.effect(payload(option), world.ctx())
                self.assertEqual(set(world.countries), {'TUN', 'FRA'})
                self.assertEqual(land.owner, 'TUN')
                self.assertEqual(world.countries['TUN'].infamy, 0)
                self.assertNotIn(COOLDOWN, world.countries['TUN'].modifiers)

    def test_new_posts_provincialize_in_place_and_replace_laissez_faire(self):
        for region in EUROPE:
            with self.subTest(region=region['key']):
                world, land = self.world(region, colonial_policy='law_type:law_internal_colonization')
                subject = self.found(world, region)
                subject.treasury = 7654
                subject.gdp = 876543
                subject.liberty_desire = 34
                fleet = Fleet(subject.tag)
                subject.fleets.append(fleet)
                cultures = set(subject.primary_cultures)
                self.assertEqual(subject.laws & ECONOMIC_LAWS, {'law_type:law_laissez_faire'})
                world.countries['TUN'].modifiers.discard(COOLDOWN)
                world.countries['TUN'].journals.add(JOURNAL)
                button = world.defs[f"crb_provincialize_{subject.tag}_button"]
                self.assertTrue(world.conditions(get(button, 'possible'), world.ctx()))
                world.effect(get(button, 'effect'), world.ctx())
                self.assertIs(world.countries[subject.tag], subject)
                self.assertEqual(subject.laws & ECONOMIC_LAWS, {'law_type:law_agrarianism'})
                self.assertTrue({'law_type:law_subjecthood', 'law_type:law_frontier_colonization'} <= subject.laws)
                self.assertEqual(subject.primary_cultures, cultures)
                self.assertEqual((subject.treasury, subject.gdp, subject.liberty_desire), (7654, 876543, 34))
                self.assertIs(subject.fleets[0], fleet)
                self.assertEqual(land.owner, subject.tag)
                self.assertEqual(subject.pact, 'crb_province')
                self.assertEqual(world.countries['TUN'].infamy, region['infamy'])
                self.assertFalse(world.conditions(get(button, 'visible'), world.ctx()))
                self.assertTrue(world.conditions(get(world.defs[f'crb_expand_{subject.tag}_province_button'], 'visible'),
                                                 world.ctx()))

    def test_bulk_expansion_handles_all_new_regions_but_keeps_colonies_and_foreign_parts(self):
        world = World(self.scripts)
        world.country('FRA')
        completed, colonies, foreign = [], [], []
        for index, region in enumerate(EUROPE):
            flags = {'crb_carthaginian_subject'} | ({'crb_province'} if index % 2 else set())
            world.country(region['tag'], overlord='TUN', variables=flags)
            completed.append((world.land(region['capital']), region['tag']))
            colonies.append(world.land(region['capital'], under_colonization=True))
            foreign.append(world.land(region['capital'], owner='FRA'))
        world.effect(world.defs['crb_expand_trading_posts_effect'], world.ctx())
        self.assertTrue(all(state.owner == tag for state, tag in completed))
        self.assertTrue(all(state.owner == 'TUN' for state in colonies))
        self.assertTrue(all(state.owner == 'FRA' for state in foreign))
        self.assertFalse(world.conditions(world.defs['crb_can_expand_trading_posts_trigger'], world.ctx()))
        self.assertEqual(world.states[0].owner, 'TUN')

    def test_existing_new_subjects_restore_journal_but_foreign_independent_and_unmarked_do_not(self):
        for region in EUROPE:
            for province in (False, True):
                with self.subTest(region=region['key'], province=province):
                    world = World(self.scripts)
                    world.country('FRA')
                    flags = {'crb_carthaginian_subject'} | ({'crb_province'} if province else set())
                    subject = world.country(region['tag'], overlord='TUN', variables=flags)
                    world.land(region['capital'], owner=region['tag'])
                    for _ in range(2):
                        world.effect(world.defs['crb_try_unlock_territorial_journal_effect'], world.ctx())
                    self.assertIn(JOURNAL, world.countries['TUN'].journals)
                    self.assertEqual(world.unlocked, 1)
                    land = world.land(region['capital'])
                    key = f"crb_expand_{region['tag']}_{'province' if province else 'post'}_button"
                    for invalid in ('foreign', 'independent', 'unmarked'):
                        subject.overlord = 'FRA' if invalid == 'foreign' else '' if invalid == 'independent' else 'TUN'
                        subject.variables = set() if invalid == 'unmarked' else set(flags)
                        button = world.defs[key]
                        self.assertFalse(world.conditions(get(button, 'visible'), world.ctx()))
                        self.assertFalse(world.conditions(get(button, 'possible'), world.ctx()))
                        world.effect(get(button, 'effect'), world.ctx())
                        self.assertEqual(land.owner, 'TUN')

    def test_both_country_forms_have_localized_names_and_resolvable_distinct_flag_bindings(self):
        names = [node for path, nodes in self.scripts.items()
                 if path.startswith('common/dynamic_country_names/') for node in nodes]
        flags = [node for path, nodes in self.scripts.items()
                 if path.startswith('common/flag_definitions/') for node in nodes]
        coats = {node.key for path, nodes in self.scripts.items()
                 if path.startswith('common/coat_of_arms/') for node in nodes if isinstance(node, Node)}
        for region in EUROPE:
            for province in (False, True):
                with self.subTest(region=region['key'], province=province):
                    world, _ = self.world(region)
                    subject = self.found(world, region, province)
                    world.saved['actor'] = subject
                    dynamic = get(get(names, subject.tag), 'dynamic_country_name')
                    merchant = world.conditions(get(dynamic, 'trigger'), world.ctx())
                    self.assertEqual(merchant, not province)
                    name_key = get(dynamic, 'name') if merchant else subject.tag
                    for language, values in self.locales.items():
                        ending = ('行省' if province else '商站') if language == 'simp_chinese' else ('Province' if province else 'Trading Post')
                        self.assertTrue(values[name_key].endswith(ending), values[name_key])
                    candidates = [node.value for node in entries(get(flags, subject.tag), 'flag_definition')
                                  if world.conditions(get(node.value, 'trigger', []), world.ctx())]
                    selected = max(candidates, key=lambda ns: int(get(ns, 'priority')))
                    self.assertEqual(get(selected, 'coa'), f'crb_{subject.tag}' + ('' if province else '_trading_post'))
                    self.assertIn(get(selected, 'coa'), coats)
                    self.assertIn(get(selected, 'subject_canton'), coats)
                    subject.overlord = ''
                    self.assertFalse(world.conditions(get(dynamic, 'trigger'), world.ctx()))
