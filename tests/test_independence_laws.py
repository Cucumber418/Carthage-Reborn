"""All former territorial subjects choose governance once per independence cycle."""
import unittest

from test_territories import GOVERNANCE_LAWS, Node, World, entries, get, load_scripts

MARKER = 'crb_carthaginian_subject'
PENDING = 'crb_independence_choice_pending'
DONE = 'crb_independence_choice_done'
CYCLE = 'crb_independence_choice_cycle'
CAPTURED = 'crb_independence_choice_request_cycle'
INITIALIZED = 'crb_governor_rule_initialized'
GOVERNOR = 'law_type:law_crb_governor_rule'
CHOICE = 'crb_independence.1'
REQUEST = 'crb_try_request_independence_choice_effect'
CHOICES = {
    'a': 'law_type:law_parliamentary_republic',
    'b': 'law_type:law_presidential_republic',
    'c': 'law_type:law_monarchy',
    'e': 'law_type:law_corporate_state',
    'g': 'law_type:law_council_republic',
    'h': 'law_type:law_theocracy',
}
OTHER_LAWS = {'law_type:law_subjecthood', 'law_type:law_frontier_colonization',
              'law_type:law_agrarianism', 'law_type:law_state_religion'}


def payload(option):
    return [node for node in option if node.key not in
            ('name', 'trigger', 'default_option', 'show_as_unavailable', 'ai_chance')]


class ChoiceWorld(World):
    """Model the exact native strongest-government-IG gate used by these choices."""
    def __init__(self, scripts):
        super().__init__(scripts)
        self.strongest_in_government = True
        self.approved_governance = set()
        self.factory_councils = False

    def condition(self, node, ctx):
        if node.key == 'any_interest_group':
            expected = {'is_in_government', 'is_strongest_ig_in_government', 'law_stance'}
            if {item.key for item in node.value} != expected:
                raise AssertionError(('Unexpected interest group gate', node.value))
            if get(node.value, 'is_in_government') != 'yes' or get(node.value, 'is_strongest_ig_in_government') != 'yes':
                raise AssertionError(('Unexpected interest group membership', node.value))
            stance = get(node.value, 'law_stance')
            value = entries(stance, 'value')
            if len(value) != 1 or value[0].op != '>=' or value[0].value != 'approve':
                raise AssertionError(('Unexpected law stance gate', stance))
            return self.strongest_in_government and get(stance, 'law') in self.approved_governance
        if node.key == 'has_factory_councils_law_or_amendment':
            if node.value not in ('yes', 'no'):
                raise AssertionError(('Unexpected factory councils predicate', node.value))
            return self.factory_councils == (node.value == 'yes')
        return super().condition(node, ctx)


class IndependenceGovernmentChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts = load_scripts()
        cls.tags = sorted(tag for tag in World(cls.scripts).country_definitions if tag != 'TUN')
        if len(cls.tags) != 25:
            raise AssertionError('Expected all 25 territorial country definitions')

    def country(self, tag='NUM', province=False, law=GOVERNOR, independent=True, marked=True):
        world = ChoiceWorld(self.scripts)
        flags = ({MARKER, INITIALIZED} if marked else set()) | ({'crb_province'} if province else set())
        country = world.country(tag, variables=flags, laws=OTHER_LAWS | {law},
                                overlord='' if independent else 'TUN',
                                primary_cultures={'crb_punic', 'berber'},
                                treasury=12345, gdp=654321, liberty_desire=42)
        world.land('STATE_ORAN', owner=tag)
        return world, country

    def callback(self, world, tag, hook):
        callbacks = get(world.defs.get(hook, []), 'on_actions', [])
        expected = 'crb_on_territory_independence' if hook == 'on_become_independent' else 'crb_on_territory_subjecthood'
        self.assertIn(expected, callbacks)
        for key in callbacks:
            definition = world.defs[key]
            if world.conditions(get(definition, 'trigger', []), world.ctx(tag)):
                world.effect(get(definition, 'effect', []), world.ctx(tag))

    def monthly(self, world, tag):
        world.effect(get(world.defs['crb_monthly_pulse_subject'], 'effect'), world.ctx(tag))

    def request(self, world, tag):
        self.callback(world, tag, 'on_become_independent')

    def option(self, world, suffix):
        return next(node.value for node in entries(world.defs[CHOICE], 'option')
                    if get(node.value, 'name') == CHOICE + '.' + suffix)

    def use_window(self, world, window, suffix):
        key, tag, saved = window
        self.assertEqual(key, CHOICE)
        prior = world.saved
        world.saved = dict(saved)
        try:
            option = self.option(world, suffix)
            self.assertTrue(world.conditions(get(option, 'trigger', []), world.ctx(tag)))
            world.effect(payload(option), world.ctx(tag))
        finally:
            world.saved = prior

    def test_all_country_forms_and_current_laws_queue_one_choice_without_automatic_law_change(self):
        for tag in self.tags:
            for province in (False, True):
                for law in sorted(GOVERNANCE_LAWS):
                    with self.subTest(tag=tag, province=province, law=law):
                        world, country = self.country(tag, province, law)
                        before = set(country.laws)
                        self.request(world, tag)
                        self.request(world, tag)
                        self.monthly(world, tag)
                        self.assertEqual(country.laws, before)
                        self.assertIn(PENDING, country.variables)
                        self.assertNotIn(DONE, country.variables)
                        self.assertEqual(len(world.scheduled_days), 1)
                        key, days, actor, saved = world.scheduled_days[0]
                        self.assertEqual((key, days, actor), (CHOICE, 1, tag))
                        self.assertEqual(saved[CAPTURED], country.variable_values[CYCLE])
                        world.fire_scheduled_day_events()
                        self.assertEqual(world.events, [CHOICE])
                        self.assertEqual(country.laws, before)
                        self.assertEqual((country.treasury, country.gdp, country.liberty_desire), (12345, 654321, 42))
                        self.assertFalse(world.countries['TUN'].laws)

    def test_each_government_choice_applies_one_law_and_finishes_only_once(self):
        for tag in self.tags:
            for province in (False, True):
                for suffix, law in CHOICES.items():
                    with self.subTest(tag=tag, province=province, option=suffix):
                        world, country = self.country(tag, province,
                            GOVERNOR if province else 'law_type:law_crb_dual_sufetes')
                        self.request(world, tag)
                        world.fire_scheduled_day_events()
                        window = world.event_contexts[-1]
                        world.approved_governance.add(law)
                        world.factory_councils = True
                        self.use_window(world, window, suffix)
                        self.assertEqual(country.laws & GOVERNANCE_LAWS, {law})
                        self.assertEqual(country.laws - GOVERNANCE_LAWS, OTHER_LAWS)
                        self.assertNotIn(PENDING, country.variables)
                        self.assertIn(DONE, country.variables)
                        self.assertEqual(country.primary_cultures, {'crb_punic', 'berber'})
                        self.assertIn(MARKER, country.variables)
                        self.assertEqual('crb_province' in country.variables, province)
                        # Reusing a stale event window cannot select a different law afterward.
                        self.use_window(world, window, 'b' if suffix == 'a' else 'a')
                        self.assertEqual(country.laws & GOVERNANCE_LAWS, {law})
                        self.monthly(world, tag)
                        self.request(world, tag)
                        self.assertFalse(world.scheduled_days)
                        self.assertIsNone(get(world.defs[CHOICE], 'after'))

    def test_native_option_gates_are_retained_and_factory_councils_is_not_ignored(self):
        world, country = self.country()
        self.request(world, country.tag)
        world.fire_scheduled_day_events()
        world.saved = dict(world.event_contexts[-1][2])
        original = world.defs['independence.2']
        for suffix, law in CHOICES.items():
            option = self.option(world, suffix)
            native = next(node.value for node in entries(original, 'option')
                          if get(node.value, 'name') == 'independence.2.' + suffix)
            self.assertEqual(get(option, 'trigger', []), get(native, 'trigger', []))
            world.approved_governance.clear()
            world.factory_councils = False
            self.assertEqual(world.conditions(get(option, 'trigger', []), world.ctx(country.tag)), suffix in ('a', 'b'))
            world.approved_governance.add(law)
            if suffix == 'g':
                self.assertFalse(world.conditions(get(option, 'trigger'), world.ctx(country.tag)))
            world.factory_councils = True
            self.assertTrue(world.conditions(get(option, 'trigger', []), world.ctx(country.tag)))
            if suffix not in ('a', 'b'):
                world.strongest_in_government = False
                self.assertFalse(world.conditions(get(option, 'trigger'), world.ctx(country.tag)))
                world.strongest_in_government = True

    def test_subjects_and_unmarked_countries_never_request_a_choice(self):
        for independent, marked in ((False, True), (False, False), (True, False)):
            with self.subTest(independent=independent, marked=marked):
                world, country = self.country(independent=independent, marked=marked)
                before = set(country.laws)
                self.request(world, country.tag)
                world.effect(world.defs[REQUEST], world.ctx(country.tag))
                self.assertEqual(country.laws, before)
                self.assertFalse(world.scheduled_days)
                self.assertNotIn(PENDING, country.variables)
                self.assertNotIn(DONE, country.variables)
        world = ChoiceWorld(self.scripts)
        world.effect(world.defs[REQUEST], world.ctx())
        self.assertFalse(world.scheduled_days)

    def test_monthly_fallback_requests_once_and_clears_a_missed_subject_transition_once(self):
        for flag in (PENDING, DONE):
            with self.subTest(old_flag=flag):
                world, country = self.country(independent=False)
                country.variables.update({flag, CYCLE})
                country.variable_values[CYCLE] = 7
                before = set(country.laws)
                self.monthly(world, country.tag)
                self.assertEqual(country.laws, before)
                self.assertNotIn(PENDING, country.variables)
                self.assertNotIn(DONE, country.variables)
                self.assertEqual(country.variable_values[CYCLE], 8)
                self.monthly(world, country.tag)
                self.assertEqual(country.variable_values[CYCLE], 8)
                country.overlord = ''
                self.monthly(world, country.tag)
                self.monthly(world, country.tag)
                self.assertEqual(len(world.scheduled_days), 1)
                self.assertEqual(world.scheduled_days[0][3][CAPTURED], 8)
                self.assertEqual(country.laws, before)

    def test_rapid_resubjugation_invalidates_the_old_queued_event_before_it_is_shown(self):
        world, country = self.country()
        self.request(world, country.tag)
        old = dict(world.scheduled_days[0][3])
        country.overlord = 'TUN'
        self.callback(world, country.tag, 'on_become_subject')
        country.overlord = ''
        self.request(world, country.tag)
        self.assertEqual(len(world.scheduled_days), 2)
        self.assertNotEqual(old[CAPTURED], world.scheduled_days[1][3][CAPTURED])
        world.fire_scheduled_day_events()
        self.assertEqual(world.events, [CHOICE])
        self.assertEqual(world.event_contexts[-1][2][CAPTURED], country.variable_values[CYCLE])
        self.use_window(world, world.event_contexts[-1], 'a')
        self.assertIn(DONE, country.variables)

    def test_stale_open_window_cannot_change_laws_or_finish_the_new_cycle(self):
        world, country = self.country()
        self.request(world, country.tag)
        world.fire_scheduled_day_events()
        old_window = world.event_contexts[-1]
        country.overlord = 'TUN'
        self.callback(world, country.tag, 'on_become_subject')
        country.overlord = ''
        self.request(world, country.tag)
        prior = world.saved
        world.saved = dict(old_window[2])
        self.assertTrue(world.conditions(get(world.defs[CHOICE], 'cancellation_trigger'), world.ctx(country.tag)))
        world.saved = prior
        before = set(country.laws)
        self.use_window(world, old_window, 'a')
        self.assertEqual(country.laws, before)
        self.assertIn(PENDING, country.variables)
        self.assertNotIn(DONE, country.variables)
        world.fire_scheduled_day_events()
        self.use_window(world, world.event_contexts[-1], 'b')
        self.assertEqual(country.laws & GOVERNANCE_LAWS, {CHOICES['b']})
        self.use_window(world, old_window, 'a')
        self.assertEqual(country.laws & GOVERNANCE_LAWS, {CHOICES['b']})

    def test_queued_choice_is_cancelled_if_country_is_a_subject_again_or_loses_the_marker(self):
        for reason in ('subject', 'unmarked'):
            with self.subTest(reason=reason):
                world, country = self.country()
                before = set(country.laws)
                self.request(world, country.tag)
                if reason == 'subject':country.overlord = 'TUN'
                else:country.variables.discard(MARKER)
                world.fire_scheduled_day_events()
                self.assertFalse(world.events)
                self.assertEqual(country.laws, before)

    def test_completed_choice_stays_done_until_a_real_subject_transition(self):
        world, country = self.country()
        self.request(world, country.tag)
        world.fire_scheduled_day_events()
        self.use_window(world, world.event_contexts[-1], 'a')
        world.effect([Node('activate_law', '=', GOVERNOR)], world.ctx(country.tag))
        self.monthly(world, country.tag)
        self.request(world, country.tag)
        self.assertFalse(world.scheduled_days)
        self.assertEqual(country.laws & GOVERNANCE_LAWS, {GOVERNOR})
        country.overlord = 'TUN'
        self.callback(world, country.tag, 'on_become_subject')
        country.overlord = ''
        self.request(world, country.tag)
        self.assertNotIn(DONE, country.variables)
        world.fire_scheduled_day_events()
        world.approved_governance.add(CHOICES['h'])
        self.use_window(world, world.event_contexts[-1], 'h')
        self.assertEqual(country.laws & GOVERNANCE_LAWS, {CHOICES['h']})
