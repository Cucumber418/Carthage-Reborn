"""Exercise actual faction outcomes and recover unfinished Hannibal requests."""
from dataclasses import dataclass
import unittest

from test_territories import Node, World, entries, get, load_scripts
from test_gaul_and_governance import payload

JOURNAL = 'je_crb_hannibal_returns'
INTRO = 'crb_hannibal.0'
NOTICE = 'crb_hanno_barca.2'
PENDING = 'crb_hannibal_intro_pending'
STARTED = 'crb_hannibal_route_started'
SHOWN = 'crb_hannibal_intro_shown'
REWARDS = 'crb_hannibal_intro_rewards_granted'


@dataclass
class FactionJournal:
    progress: int


class FactionWorld(World):
    def __init__(self, scripts):
        super().__init__(scripts)
        self.victory_modifier_applications = 0

    def condition(self, node, ctx):
        if node.key == '"scripted_bar_progress(crb_hanno_barca_progress_bar)"':
            return self.compare(ctx.obj.progress, node.op, float(node.value))
        if node.key == 'var:crb_hb_elapsed_months':
            return self.compare(ctx.obj.variable_values['crb_hb_elapsed_months'], node.op, float(node.value))
        return super().condition(node, ctx)

    def effect(self, nodes, ctx):
        for node in nodes:
            if node.key == 'add_modifier' and get(node.value, 'name') == 'crb_popular_assembly_restored':
                self.victory_modifier_applications += 1
            super().effect([node], ctx)


class DeferredJournalWorld(FactionWorld):
    """Model a journal whose registration is visible after the opening request."""
    def __init__(self, scripts):
        super().__init__(scripts)
        self.defer_journal = True
        self.requested_journal = False

    def effect(self, nodes, ctx):
        for node in nodes:
            if node.key == 'add_journal_entry' and get(node.value, 'type') == JOURNAL and self.defer_journal:
                self.requested_journal = True
            else:
                super().effect([node], ctx)

    def register_journal(self):
        if not self.requested_journal:
            raise AssertionError('The route helper never requested its journal')
        self.defer_journal = False
        super().effect([Node('add_journal_entry', '=', [Node('type', '=', JOURNAL)])], self.ctx())


class AutoActivatingFactionWorld(FactionWorld):
    """Let the native journal manager react to each country-variable mutation."""
    def effect(self, nodes, ctx):
        for node in nodes:
            super().effect([node], ctx)
            if node.key not in ('set_variable', 'remove_variable'):
                continue
            if ctx.obj is not self.countries['TUN'] or JOURNAL in ctx.obj.journals:
                continue
            if self.conditions(get(self.defs[JOURNAL], 'possible'), ctx):
                super().effect([Node('add_journal_entry', '=', [Node('type', '=', JOURNAL)])], ctx)


class BarcaOpeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()

    def execute(self, world, key):
        world.effect(world.defs[key], world.ctx())

    def confirm(self, world):
        world.effect(payload(entries(world.defs[NOTICE], 'option')[0].value), world.ctx())

    def assert_opened_once(self, world):
        country = world.countries['TUN']
        self.assertIn('crb_hanno_barca_concluded', country.variables)
        self.assertIn('crb_barca_victory', country.variables)
        self.assertIn(JOURNAL, country.journals)
        self.assertEqual(world.events.count(INTRO), 1)
        self.assertIn(SHOWN, country.variables)
        self.assertIn(STARTED, country.variables)
        self.assertNotIn(PENDING, country.variables)

    def test_actual_full_bar_outcome_starts_route_before_victory_notice_is_accepted(self):
        world = FactionWorld(self.scripts)
        world.saved['journal_entry'] = FactionJournal(100)
        outcome = entries(world.defs['je_crb_hanno_barca'], 'outcome')[0].value
        self.assertTrue(world.conditions(get(outcome, 'trigger'), world.ctx()))
        world.effect(get(outcome, 'effect'), world.ctx())
        self.assert_opened_once(world)
        self.assertIn(NOTICE, world.events)
        self.confirm(world)
        self.assert_opened_once(world)
        self.assertEqual(world.victory_modifier_applications, 1)

    def test_actual_three_year_barca_advantage_starts_route_before_confirmation(self):
        world = FactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.add('crb_hb_elapsed_months')
        country.variable_values['crb_hb_elapsed_months'] = 36
        world.saved['journal_entry'] = FactionJournal(80)
        outcome = entries(world.defs['je_crb_hanno_barca'], 'outcome')[2].value
        self.assertTrue(world.conditions(get(outcome, 'trigger'), world.ctx()))
        world.effect(get(outcome, 'effect'), world.ctx())
        self.assert_opened_once(world)
        self.assertIn(NOTICE, world.events)
        self.confirm(world)
        self.assert_opened_once(world)
        self.assertEqual(world.victory_modifier_applications, 1)

    def test_standalone_victory_notice_confirmation_is_complete_and_idempotent(self):
        world = FactionWorld(self.scripts)
        self.confirm(world)
        self.assert_opened_once(world)
        self.confirm(world)
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)
        self.assertEqual(world.victory_modifier_applications, 1)

    def test_a_started_only_legacy_request_does_not_count_as_an_actual_opening(self):
        world = FactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.update(('crb_barca_victory', 'crb_hanno_barca_concluded',
                                  'crb_hannibal_route_open', STARTED))
        possible = get(world.defs[JOURNAL], 'possible')
        self.assertFalse(world.conditions(possible, world.ctx()))
        country.variables.add(PENDING)
        self.assertTrue(world.conditions(possible, world.ctx()))
        country.variables.remove(PENDING)
        self.confirm(world)
        self.assert_opened_once(world)

    def test_deferred_journal_registration_does_not_create_false_opening_history(self):
        world = DeferredJournalWorld(self.scripts)
        country = world.countries['TUN']
        self.confirm(world)
        self.assertTrue(world.requested_journal)
        self.assertIn(PENDING, country.variables)
        self.assertNotIn(STARTED, country.variables)
        self.assertNotIn(SHOWN, country.variables)
        self.assertNotIn(JOURNAL, country.journals)
        self.assertEqual(world.events.count(INTRO), 0)
        world.register_journal()
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)

    def test_pending_request_with_existing_journal_finishes_once(self):
        world = FactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.update(('crb_barca_victory', 'crb_hanno_barca_concluded',
                                  'crb_hannibal_route_open', PENDING))
        country.journals.add(JOURNAL)
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)
        self.assertEqual(world.unlocked, 0)
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)

    def test_actual_opening_rewards_progress_and_completion_still_never_replay(self):
        flags = (SHOWN, REWARDS, 'crb_hannibal_concluded') + tuple(
            'crb_hannibal_' + target + '_done'
            for target in ('tripoli', 'numidia', 'syracuse', 'islands', 'iberia', 'new_carthage', 'tyre'))
        for flag in flags:
            with self.subTest(history=flag):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(('crb_barca_victory', 'crb_hanno_barca_concluded', flag))
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assertEqual(world.events.count(INTRO), 0)
                self.assertNotIn(JOURNAL, country.journals)
                self.assertIn(flag, country.variables)
        world = FactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.update(('crb_barca_victory', 'crb_hanno_barca_concluded'))
        country.modifiers.add('crb_hannibal_returned')
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assertNotIn(JOURNAL, country.journals)
        self.assertNotIn(INTRO, world.events)

    def test_manual_repair_recovers_only_unsettled_inactive_requests_and_is_idempotent(self):
        eligible = {'crb_barca_victory', 'crb_hanno_barca_concluded'}
        for stale in ({STARTED}, {SHOWN}, {STARTED, SHOWN, PENDING}):
            with self.subTest(stale_request=stale):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(eligible | stale)
                self.execute(world, 'crb_repair_hannibal_start_effect')
                self.assert_opened_once(world)
                self.execute(world, 'crb_repair_hannibal_start_effect')
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assert_opened_once(world)

        world = AutoActivatingFactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.update(eligible | {'crb_hannibal_route_open', STARTED, SHOWN})
        self.assertNotIn(PENDING, country.variables)
        self.assertFalse(world.conditions(get(world.defs[JOURNAL], 'possible'), world.ctx()))
        self.execute(world, 'crb_repair_hannibal_start_effect')
        self.assert_opened_once(world)
        self.assertEqual(world.unlocked, 1)
        self.execute(world, 'crb_try_start_hannibal_route_effect')
        self.assert_opened_once(world)

        settled = (REWARDS, 'crb_hannibal_concluded') + tuple(
            'crb_hannibal_' + target + '_done'
            for target in ('tripoli', 'numidia', 'syracuse', 'islands', 'iberia', 'new_carthage', 'tyre'))
        for flag in settled + ('crb_hannibal_returned',):
            with self.subTest(settled_history=flag):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(eligible | {STARTED, SHOWN, PENDING})
                if flag == 'crb_hannibal_returned':
                    country.modifiers.add(flag)
                else:
                    country.variables.add(flag)
                before = set(country.variables)
                self.execute(world, 'crb_repair_hannibal_start_effect')
                self.assertEqual(country.variables, before)
                self.assertNotIn(JOURNAL, country.journals)
                self.assertNotIn(INTRO, world.events)

        world = FactionWorld(self.scripts)
        country = world.countries['TUN']
        country.variables.update(eligible | {PENDING})
        country.journals.add(JOURNAL)
        self.execute(world, 'crb_repair_hannibal_start_effect')
        self.assertIn(PENDING, country.variables)
        self.assertEqual(country.journals, {JOURNAL})
        self.assertNotIn(INTRO, world.events)
        self.assertEqual(world.unlocked, 0)

        for faction_flags in (set(), {'crb_hanno_victory', 'crb_hanno_barca_concluded'}):
            with self.subTest(ineligible_faction=faction_flags):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(faction_flags | {STARTED, SHOWN})
                before = set(country.variables)
                self.execute(world, 'crb_repair_hannibal_start_effect')
                self.assertEqual(country.variables, before)
                self.assertNotIn(JOURNAL, country.journals)
                self.assertNotIn(INTRO, world.events)

    def test_unshown_pending_opening_survives_progress_before_the_route_retry(self):
        eligible = {'crb_barca_victory', 'crb_hanno_barca_concluded', 'crb_hannibal_route_open'}
        for target in ('tripoli', 'numidia', 'syracuse', 'islands', 'iberia', 'new_carthage', 'tyre'):
            progress = 'crb_hannibal_' + target + '_done'
            with self.subTest(new_pending_progress=target):
                world = DeferredJournalWorld(self.scripts)
                country = world.countries['TUN']
                self.confirm(world)
                self.assertIn(PENDING, country.variables)
                self.assertNotIn(INTRO, world.events)
                world.register_journal()
                # A journal monthly pulse can record a completed target before the country retry.
                country.variables.add(progress)
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assert_opened_once(world)
                self.assertIn(progress, country.variables)
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assert_opened_once(world)

            with self.subTest(old_progress_without_request=target):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(eligible | {progress})
                country.journals.add(JOURNAL)
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assertNotIn(INTRO, world.events)
                self.assertNotIn(PENDING, country.variables)
                self.assertIn(JOURNAL, country.journals)

            with self.subTest(old_inactive_progress_with_stale_request=target):
                world = FactionWorld(self.scripts)
                country = world.countries['TUN']
                country.variables.update(eligible | {PENDING, progress})
                self.execute(world, 'crb_try_start_hannibal_route_effect')
                self.assertNotIn(INTRO, world.events)
                self.assertNotIn(JOURNAL, country.journals)
                self.assertIn(progress, country.variables)
                self.assertEqual(world.unlocked, 0)

            for actual_history in (SHOWN, REWARDS, 'crb_hannibal_concluded', 'crb_hannibal_returned'):
                with self.subTest(pending_with_real_history=(target, actual_history)):
                    world = FactionWorld(self.scripts)
                    country = world.countries['TUN']
                    country.variables.update(eligible | {PENDING, progress})
                    if actual_history == 'crb_hannibal_returned':
                        country.modifiers.add(actual_history)
                    else:
                        country.variables.add(actual_history)
                    country.journals.add(JOURNAL)
                    self.execute(world, 'crb_try_start_hannibal_route_effect')
                    self.assertNotIn(INTRO, world.events)
                    self.assertIn(progress, country.variables)
