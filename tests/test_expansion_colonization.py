"""Exercise expansion eligibility and execution against changing colony states."""
import unittest

from test_territories import Node, World, get, load_scripts
from territory_test_data import EUROPE, TOTAL_REGIONS, buttons


REGIONS = {
    'TRP': 'STATE_TRIPOLI',
    'NUM': 'STATE_ALGIERS',
    'IBT': 'STATE_MURCIA',
    'GLT': 'STATE_PROVENCE',
    'SNT': 'STATE_SAVOY',
    'IOP': 'STATE_CAMPANIA',
    'RPR': 'STATE_CAMPANIA',
    'CPM': 'STATE_FEZ',
    'CPE': 'STATE_MIDDLE_EGYPT',
    'CPF': 'STATE_LEBANON',
    'CPS': 'STATE_ALEPPO',
    'CPB': 'STATE_MOSUL',
    'CPA': 'STATE_YEMEN',
}

REGIONS.update({region['tag']: region['capital'] for region in EUROPE})


class ExpansionColonizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()
        cls.buttons = buttons(cls.scripts, 'crb_expand_')
        if len(cls.buttons) != TOTAL_REGIONS * 2:
            raise AssertionError('Expected both expansion buttons for every territorial region')

    def world(self, tag, province):
        world = World(self.scripts)
        world.countries['TUN'].journals.add('je_crb_territories')
        world.countries['TUN'].variables.add('crb_territories_unlocked')
        flags = {'crb_carthaginian_subject'} | ({'crb_province'} if province else set())
        world.country(tag, overlord='TUN', variables=flags)
        world.country('FRA')
        return world

    def button_world(self, button):
        tag = button.key.split('_')[2]
        world = self.world(tag, '_province_' in button.key)
        self.assertTrue(world.conditions(get(button.value, 'visible'), world.ctx()))
        return world, tag, REGIONS[tag]

    def execute_button(self, world, button):
        world.effect(get(button.value, 'effect'), world.ctx())

    def bulk_possible(self, world):
        return world.conditions(get(world.defs['crb_expand_trading_posts_decision'], 'possible'), world.ctx())

    def execute_bulk(self, world):
        # Also exercise the guarded effect directly, bypassing a stale UI decision.
        world.effect(world.defs['crb_expand_trading_posts_effect'], world.ctx())

    def test_all_buttons_wait_for_colonization_to_finish(self):
        for button in self.buttons:
            with self.subTest(button=button.key):
                world, tag, region = self.button_world(button)
                colony = world.land(region, under_colonization=True)
                self.assertFalse(world.conditions(get(button.value, 'possible'), world.ctx()))
                self.execute_button(world, button)
                self.assertEqual(colony.owner, 'TUN')
                colony.under_colonization = False
                self.assertTrue(world.conditions(get(button.value, 'possible'), world.ctx()))
                self.execute_button(world, button)
                self.assertEqual(colony.owner, tag)

    def test_all_buttons_transfer_completed_land_and_preserve_colonies_foreign_parts_and_capitals(self):
        for button in self.buttons:
            with self.subTest(button=button.key):
                world, tag, region = self.button_world(button)
                completed = world.land(region)
                colony = world.land(region, under_colonization=True)
                foreign = world.land(region, owner='FRA')
                capital = world.land(region, capital=True)
                self.assertTrue(world.conditions(get(button.value, 'possible'), world.ctx()))
                self.execute_button(world, button)
                self.assertEqual((completed.owner, colony.owner, foreign.owner, capital.owner),
                                 (tag, 'TUN', 'FRA', 'TUN'))
                self.assertEqual(world.states[0].owner, 'TUN')

    def test_all_buttons_revalidate_each_state_after_the_button_was_available(self):
        for button in self.buttons:
            with self.subTest(button=button.key):
                world, tag, region = self.button_world(button)
                newly_colonizing = world.land(region)
                completed = world.land(region)
                self.assertTrue(world.conditions(get(button.value, 'possible'), world.ctx()))
                newly_colonizing.under_colonization = True
                # Another completed state keeps the effect executable, so its own filter matters.
                self.assertTrue(world.conditions(get(button.value, 'possible'), world.ctx()))
                self.execute_button(world, button)
                self.assertEqual((newly_colonizing.owner, completed.owner), ('TUN', tag))

    def test_bulk_expansion_waits_for_colonization_to_finish_for_every_subject_region(self):
        for tag, region in REGIONS.items():
            for province in (False, True):
                with self.subTest(tag=tag, province=province):
                    world = self.world(tag, province)
                    colony = world.land(region, under_colonization=True)
                    self.assertFalse(self.bulk_possible(world))
                    self.execute_bulk(world)
                    self.assertEqual(colony.owner, 'TUN')
                    colony.under_colonization = False
                    self.assertTrue(self.bulk_possible(world))
                    self.execute_bulk(world)
                    self.assertEqual(colony.owner, tag)

    def test_bulk_expansion_filters_colonies_and_rechecks_state_changes_in_every_subject_region(self):
        for tag, region in REGIONS.items():
            for province in (False, True):
                with self.subTest(tag=tag, province=province):
                    world = self.world(tag, province)
                    completed = world.land(region)
                    colony = world.land(region, under_colonization=True)
                    newly_colonizing = world.land(region)
                    foreign = world.land(region, owner='FRA')
                    capital = world.land(region, capital=True)
                    self.assertTrue(self.bulk_possible(world))
                    newly_colonizing.under_colonization = True
                    self.assertTrue(self.bulk_possible(world))
                    self.execute_bulk(world)
                    self.assertEqual((completed.owner, colony.owner, newly_colonizing.owner,
                                      foreign.owner, capital.owner),
                                     (tag, 'TUN', 'TUN', 'FRA', 'TUN'))
                    self.assertEqual(world.states[0].owner, 'TUN')
