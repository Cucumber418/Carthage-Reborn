"""Option previews, real monetary effects, and recurring policy transitions."""
import unittest
from test_localization import load_localization
from test_territories import Node,World,entries,get,load_scripts,subst
from test_gaul_and_governance import POLICIES,payload,walk


class EventMoneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts=load_scripts()
        cls.defs=World(cls.scripts).defs
        cls.locales={lang:load_localization(lang) for lang in ('simp_chinese','english')}

    def visible_effects(self,nodes):
        """Expand actual scripted effects, respecting engine tooltip boundaries."""
        native={'add_modifier','add_treasury','change_relations','create_bidirectional_truce'}
        for n in nodes:
            if n.key in ('hidden_effect','limit','trigger','show_as_unavailable','ai_chance'):continue
            if n.key=='custom_tooltip' or n.key in native:yield n
            elif n.key in self.defs and n.key.endswith('_effect'):
                params={p.key:p.value for p in n.value} if isinstance(n.value,list) else {}
                yield from self.visible_effects(subst(self.defs[n.key],params))
            elif isinstance(n.value,list):yield from self.visible_effects(n.value)
            else:yield n

    def test_gallic_choices_use_native_effects_and_hide_only_internal_cleanup(self):
        expected=(
            (['change_relations','create_bidirectional_truce','add_modifier','add_modifier'],
             {'crb_gallic_appeasement_expense','crb_gallic_appeasement_income'},'20'),
            (['change_relations','add_modifier'],{'crb_flavor_gallic_legacy'},'-50'),
            (['add_modifier'],{'crb_gallic_nonintervention'},None),
        )
        for option,(kinds,modifiers,relation) in zip(entries(self.defs['crb_flavor.17'],'option'),expected):
            with self.subTest(option=get(option.value,'name')):
                visible=list(self.visible_effects(payload(option.value)))
                self.assertEqual([n.key for n in visible],kinds)
                self.assertEqual({get(n.value,'name') for n in visible if n.key=='add_modifier'},modifiers)
                if relation is not None:
                    self.assertEqual(get(next(n.value for n in visible if n.key=='change_relations'),'value'),relation)
                for n in visible:
                    if n.key in ('add_modifier','create_bidirectional_truce'):
                        self.assertEqual(get(n.value,'months'),'60')

    def test_changing_from_each_old_policy_still_cleans_up_and_schedules_once(self):
        for old in POLICIES:
            for option,policy in zip(entries(self.defs['crb_flavor.17'],'option'),POLICIES):
                with self.subTest(old=old,new=policy):
                    w=World(self.scripts);w.country('FRA');w.land('STATE_ALGIERS','FRA')
                    tun=w.countries['TUN'];tun.variables.update(('crb_gallic_cycle_started','crb_gallic_choice_pending'))
                    tun.modifiers.add(old);tun.modifier_months[old]=60
                    # The engine removes the old policy at the end of its term.
                    w.effect([Node('remove_modifier','=',old)],w.ctx())
                    w.effect(payload(option.value),w.ctx())
                    self.assertEqual(tun.modifiers.intersection(POLICIES),{policy})
                    self.assertNotIn('crb_gallic_choice_pending',tun.variables)
                    self.assertEqual(w.scheduled,[('crb_flavor.17',60,'TUN')])

    def test_weekly_payment_is_rounded_identically_for_both_countries(self):
        option=entries(self.defs['crb_flavor.17'],'option')[0].value
        for gdp,expected in ((800000,960),(850000,1020),(900000,1080),(123456.49,148),(123899,149),(0,0)):
            with self.subTest(gdp=gdp):
                w=World(self.scripts);w.country('FRA',gdp=987654321);w.land('STATE_ALGIERS','FRA')
                tun=w.countries['TUN'];tun.gdp=gdp;tun.variables.add('crb_gallic_cycle_started')
                w.effect(payload(option),w.ctx())
                fra=w.countries['FRA']
                self.assertEqual((tun.treasury,fra.treasury),(0,0))
                self.assertEqual(tun.modifier_amounts['crb_gallic_appeasement_expense'],expected)
                self.assertEqual(fra.modifier_amounts['crb_gallic_appeasement_income'],expected)
                tun.gdp*=3;fra.gdp/=2
                self.assertEqual(tun.modifier_amounts['crb_gallic_appeasement_expense'],expected)
                self.assertEqual(fra.modifier_amounts['crb_gallic_appeasement_income'],expected)

    def test_french_exit_clears_both_sides_of_payment_and_preserves_truce(self):
        w=World(self.scripts);fra=w.country('FRA');land=w.land('STATE_ALGIERS','FRA')
        tun=w.countries['TUN'];tun.variables.add('crb_gallic_cycle_started')
        w.effect(payload(entries(self.defs['crb_flavor.17'],'option')[0].value),w.ctx())
        self.assertIn('crb_gallic_appeasement_income',fra.modifiers)
        land.owner='TUN';w.effect(w.defs['crb_check_french_border_effect'],w.ctx())
        self.assertNotIn('crb_gallic_appeasement_expense',tun.modifiers)
        self.assertNotIn('crb_gallic_appeasement_income',fra.modifiers)
        self.assertEqual((tun.truces['FRA'],fra.truces['TUN']),(60,60))

    def test_new_policy_clears_stale_payment_on_both_sides(self):
        for option in entries(self.defs['crb_flavor.17'],'option')[1:]:
            w=World(self.scripts);fra=w.country('FRA');w.land('STATE_ALGIERS','FRA')
            tun=w.countries['TUN'];tun.variables.add('crb_gallic_cycle_started')
            tun.modifiers.add('crb_gallic_appeasement_expense');fra.modifiers.add('crb_gallic_appeasement_income')
            w.effect(payload(option.value),w.ctx())
            self.assertNotIn('crb_gallic_appeasement_expense',tun.modifiers)
            self.assertNotIn('crb_gallic_appeasement_income',fra.modifiers)

    def test_repeat_click_does_not_extend_or_duplicate_payment(self):
        w=World(self.scripts);fra=w.country('FRA');w.land('STATE_ALGIERS','FRA')
        tun=w.countries['TUN'];tun.variables.add('crb_gallic_cycle_started')
        effects=payload(entries(self.defs['crb_flavor.17'],'option')[0].value)
        w.effect(effects,w.ctx());before=(dict(tun.modifier_amounts),dict(fra.modifier_amounts),dict(tun.relations))
        tun.gdp*=10;w.effect(effects,w.ctx())
        self.assertEqual((tun.modifier_amounts,fra.modifier_amounts,tun.relations),before)
        self.assertEqual(w.scheduled,[('crb_flavor.17',60,'TUN')])

    def test_payment_modifiers_are_opposite_budget_entries_for_sixty_months(self):
        self.assertEqual(get(self.defs['crb_gallic_appeasement_expense'],'country_expenses_add'),'1')
        self.assertEqual(get(self.defs['crb_gallic_appeasement_income'],'country_tax_income_add'),'1')
        payments=[n for n in walk(self.defs['crb_gallic_appease_france_effect']) if n.key=='add_modifier']
        self.assertEqual(len(payments),2)
        for n in payments:
            self.assertEqual(get(n.value,'months'),'60')
            self.assertEqual(get(n.value,'multiplier'),'crb_gallic_appeasement_payment')
        self.assertFalse([n for n in walk(self.defs['crb_gallic_appease_france_effect']) if n.key=='add_treasury'])

    def test_all_event_monetary_modifiers_use_native_tooltips_for_value_and_duration(self):
        count=0
        for event,nodes in self.defs.items():
            if not event.startswith('crb_flavor.') or not isinstance(nodes,list):continue
            for option in entries(nodes,'option'):
                for n in self.visible_effects(payload(option.value)):
                    if n.key!='add_modifier' or get(n.value,'multiplier') is None:continue
                    name=get(n.value,'name')
                    if not name.startswith('crb_flavor_'):continue
                    count+=1
                    self.assertIn(get(n.value,'months'),('12','36','60'))
                    for lang,values in self.locales.items():
                        with self.subTest(modifier=name,language=lang):
                            self.assertIn(name,values)
                            self.assertNotIn(name+'_effect_tt',values)
        # These exact modifier/multiplier/duration nodes now drive the engine's
        # built-in name, colored values, nested breakdown and duration display.
        self.assertEqual(count,12)

    def test_veteran_payment_executes_with_its_native_treasury_tooltip(self):
        option=entries(self.defs['crb_hanno_barca_random.10'],'option')[1].value
        payment=next(n for n in self.visible_effects(payload(option)) if n.key=='add_treasury')
        # Isolate this payment: the test harness does not model vanilla budgets.
        w=World(self.scripts);w.defs['crb_hb_veterans_bounty_cost']=[Node('value','=','-5200')]
        w.effect([payment],w.ctx());self.assertEqual(w.countries['TUN'].treasury,-5200)
        for values in self.locales.values():
            self.assertNotIn('crb_hb_veterans_bounty_effect_tt',values)

    def test_player_facing_localization_does_not_explain_money_formulas(self):
        for lang,values in self.locales.items():
            for key,text in values.items():
                with self.subTest(language=lang,key=key):
                    self.assertNotRegex(text,r'(?i)\bGDP\b|年产值|计算公式|计算方式')


if __name__=='__main__':unittest.main()
