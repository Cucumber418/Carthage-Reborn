"""Creation-time culture and law settings across every territorial foundation."""
import re
import unittest

from test_territories import World, get, load_scripts
from test_expansion_colonization import REGIONS


SETUP = 'crb_initialize_territory_culture_and_laws_effect'
SUBJECTHOOD = 'law_type:law_subjecthood'
FRONTIER = 'law_type:law_frontier_colonization'
COLONIAL_POLICIES = (
    'law_type:law_no_colonial_affairs',
    'law_type:law_internal_colonization',
    FRONTIER,
    'law_type:law_colonial_resettlement',
    'law_type:law_colonial_exploitation',
)


class SubjectFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()
        world = World(cls.scripts)
        cls.foundations = {
            key: get(nodes, 'crb_create_territory_subject_effect')
            for key, nodes in world.defs.items()
            if re.fullmatch(r'crb_create_(puppet|province)_[A-Z]+_effect', key)
        }
        if len(cls.foundations) != 24 or any(params is None for params in cls.foundations.values()):
            raise AssertionError('Expected all 24 direct trading-post/province foundation paths')

    def found(self, key, params, colonial_policy):
        world = World(self.scripts)
        founder = world.countries['TUN']
        founder.primary_cultures = {'crb_punic', 'maghrebi'}
        founder.laws = {colonial_policy, 'law_type:law_cultural_exclusion'}
        tag = get(params, 'TAG')
        world.land(REGIONS[tag])
        original_cultures = set(get(world.country_definitions[tag], 'cultures'))
        world.effect(world.defs[key], world.ctx())
        return world, world.countries[tag], original_cultures

    def test_every_foundation_adds_punic_without_replacing_local_primary_cultures(self):
        for key, params in self.foundations.items():
            with self.subTest(foundation=key):
                world, subject, original = self.found(key, params, COLONIAL_POLICIES[0])
                self.assertEqual(subject.primary_cultures, original | {'crb_punic'})
                self.assertIn(SUBJECTHOOD, subject.laws)
                self.assertIn('law_type:law_crb_governor_rule', subject.laws)
                self.assertEqual(subject.overlord, 'TUN')
                self.assertFalse(world.conditions(world.defs['crb_is_carthage_trigger'], world.ctx(subject.tag)))
                self.assertFalse(world.conditions(get(world.defs['je_crb_hanno_barca'], 'possible'),
                                                  world.ctx(subject.tag)))
                self.assertEqual(world.countries['TUN'].primary_cultures, {'crb_punic', 'maghrebi'})
                self.assertEqual(world.countries['TUN'].laws,
                                 {COLONIAL_POLICIES[0], 'law_type:law_cultural_exclusion'})

    def test_all_current_colonial_policies_choose_frontier_only_when_founder_has_colonial_affairs(self):
        for key, params in self.foundations.items():
            for policy in COLONIAL_POLICIES:
                with self.subTest(foundation=key, founder_policy=policy):
                    world, subject, _ = self.found(key, params, policy)
                    self.assertEqual(FRONTIER in subject.laws, policy != COLONIAL_POLICIES[0])
                    self.assertEqual(world.countries['TUN'].laws,
                                     {policy, 'law_type:law_cultural_exclusion'})

    def test_colonial_policy_is_read_from_saved_founder_not_the_new_subject(self):
        for founder_policy, subject_policy in ((COLONIAL_POLICIES[0], COLONIAL_POLICIES[-1]),
                                                (COLONIAL_POLICIES[-1], COLONIAL_POLICIES[0])):
            with self.subTest(founder_policy=founder_policy):
                world = World(self.scripts)
                founder = world.countries['TUN']; founder.laws = {founder_policy}
                subject = world.country('NUM', laws={subject_policy}, primary_cultures={'berber'})
                world.saved['crb_territory_origin'] = founder
                world.effect(world.defs[SETUP], world.ctx('NUM'))
                self.assertEqual(FRONTIER in subject.laws, founder_policy != COLONIAL_POLICIES[0])
                self.assertEqual(subject.primary_cultures, {'berber', 'crb_punic'})
                self.assertIn(SUBJECTHOOD, subject.laws)

    def test_later_founder_law_changes_do_not_reapply_creation_settings(self):
        for key, params in self.foundations.items():
            with self.subTest(foundation=key):
                world, subject, _ = self.found(key, params, COLONIAL_POLICIES[0])
                world.countries['TUN'].laws = {COLONIAL_POLICIES[-1]}
                world.effect(get(world.defs['crb_monthly_pulse_subject'], 'effect'), world.ctx(subject.tag))
                self.assertNotIn(FRONTIER, subject.laws)
                self.assertIn(SUBJECTHOOD, subject.laws)
