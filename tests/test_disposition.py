"""Scenario regressions for cooldown, both subject forms and GDP income.

This uses the existing script harness. Modifier expiry and rendering still need
the game engine; expiry is simulated by removing the marker after it expires.
"""
import unittest
from test_territories import Node, World, entries, get, load_scripts
from test_localization import load_chinese

COOLDOWN='crb_territory_disposition_cooldown'
REGIONS=[
    ('tripoli','STATE_TRIPOLI','TRP'),('numidia','STATE_CONSTANTINE','NUM'),
    ('iberia','STATE_MURCIA','IBT'),('gaul','STATE_PROVENCE','GLT'),
    ('alpine','STATE_PIEDMONT','SNT'),('rome','STATE_APULIA','IOP'),
    ('mauretania','STATE_FEZ','CPM'),('egypt','STATE_MIDDLE_EGYPT','CPE'),
    ('phoenicia','STATE_LEBANON','CPF'),('syria','STATE_ALEPPO','CPS'),
    ('mesopotamia','STATE_BAGHDAD','CPB'),('arabia','STATE_YEMEN','CPA'),
]
EVENTS=['crb_revenge.'+str(i) for i in (10,11,12,6,7,5)]+['crb_territories.'+str(i) for i in range(1,7)]
def walk(nodes):
    for n in nodes:
        if isinstance(n,Node):
            yield n
            if isinstance(n.value,list):yield from walk(n.value)
def payload(option):return [n for n in option if n.key not in ('name','trigger','default_option')]

class DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts();cls.locales=load_chinese()
    def setUp(self):self.w=World(self.scripts)
    def execute(self,key):self.w.effect(self.w.defs[key],self.w.ctx())
    def option(self,event,suffix):
        return next(n.value for n in entries(self.w.defs[event],'option') if get(n.value,'name')==event+'.'+suffix)
    def test_cooldown_blocks_all_twelve_regions_but_keeps_buttons_visible(self):
        for _,region,_ in REGIONS:self.w.land(region)
        self.execute('crb_try_unlock_territorial_journal_effect')
        self.w.countries['TUN'].modifiers.add(COOLDOWN)
        formation_keys={n.key for n in self.scripts['common/scripted_buttons/crb_territory_buttons.txt'] if isinstance(n,Node)}
        buttons=[n for n in entries(self.w.defs['je_crb_territories'],'scripted_button') if n.value in formation_keys]
        self.assertEqual(len(buttons),12)
        for n in buttons:
            with self.subTest(button=n.value):
                b=self.w.defs[n.value]
                self.assertTrue(self.w.conditions(get(b,'visible'),self.w.ctx()))
                self.assertFalse(self.w.conditions(get(b,'possible'),self.w.ctx()))
                self.w.effect(get(b,'effect'),self.w.ctx())
        self.assertFalse(self.w.events)
    def test_success_starts_three_months_on_the_overlord_only(self):
        self.w.land('STATE_LEBANON');self.execute('crb_create_puppet_CPF_effect')
        self.assertIn(COOLDOWN,self.w.countries['TUN'].modifiers)
        self.assertNotIn(COOLDOWN,self.w.countries['CPF'].modifiers)
        duration=[n.value for n in walk(self.w.defs['crb_create_territory_subject_effect']) if n.key=='add_modifier' and get(n.value,'name')==COOLDOWN]
        self.assertEqual(len(duration),1);self.assertEqual(get(duration[0],'months'),'3')
    def test_cancel_never_starts_cooldown_or_charges_infamy(self):
        for event in EVENTS:
            with self.subTest(event=event):
                suffix='b' if event.startswith('crb_territories.') else 'c'
                self.w.effect(payload(self.option(event,suffix)),self.w.ctx())
        self.assertNotIn(COOLDOWN,self.w.countries['TUN'].modifiers)
        self.assertEqual(self.w.countries['TUN'].infamy,0)
    def test_failed_creation_does_not_start_cooldown(self):
        for state in ('no_land','at_war','tag_exists'):
            with self.subTest(state=state):
                self.w=World(self.scripts)
                if state!='no_land':self.w.land('STATE_LEBANON')
                if state=='at_war':self.w.countries['TUN'].war=True
                if state=='tag_exists':self.w.country('CPF')
                self.execute('crb_create_province_CPF_effect')
                self.assertNotIn(COOLDOWN,self.w.countries['TUN'].modifiers)
    def test_pending_choices_cannot_charge_or_create_during_cooldown(self):
        for _,region,_ in REGIONS:self.w.land(region)
        self.w.countries['TUN'].modifiers.add(COOLDOWN)
        checked=0
        for event in EVENTS:
            for option in entries(self.w.defs[event],'option'):
                if not get(option.value,'trigger'):continue
                checked+=1
                with self.subTest(option=get(option.value,'name')):
                    self.assertFalse(self.w.conditions(get(option.value,'trigger'),self.w.ctx()))
                    self.w.effect(payload(option.value),self.w.ctx())
        self.assertEqual(checked,24)
        self.assertEqual(set(self.w.countries),{'TUN'})
        self.assertEqual(self.w.countries['TUN'].infamy,0)
    def test_another_region_is_available_when_the_cooldown_expires(self):
        self.w.land('STATE_CONSTANTINE');self.w.land('STATE_LEBANON')
        self.execute('crb_try_unlock_territorial_journal_effect')
        self.execute('crb_create_puppet_NUM_effect')
        self.execute('crb_create_province_CPF_effect');self.assertNotIn('CPF',self.w.countries)
        self.w.effect([Node('remove_modifier','=',COOLDOWN)],self.w.ctx())
        self.execute('crb_create_province_CPF_effect');self.assertIn('CPF',self.w.countries)
        self.assertIn(COOLDOWN,self.w.countries['TUN'].modifiers)
    def test_hidden_regions_offer_both_forms_with_their_correct_costs(self):
        for number,(_,region,tag) in enumerate(REGIONS[6:],1):
            for suffix,province in [('c',False),('a',True)]:
                with self.subTest(tag=tag,province=province):
                    self.w=World(self.scripts);land=self.w.land(region)
                    option=self.option('crb_territories.'+str(number),suffix)
                    self.assertTrue(self.w.conditions(get(option,'trigger'),self.w.ctx()))
                    self.w.effect(payload(option),self.w.ctx())
                    subject=self.w.countries[tag]
                    self.assertEqual(land.owner,tag);self.assertEqual(subject.overlord,'TUN')
                    self.assertEqual('crb_province' in subject.variables,province)
                    self.assertEqual(subject.pact,'crb_province' if province else 'crb_trading_post')
                    self.assertIn('law_type:law_oligarchy' if province else 'law_type:law_free_trade',subject.laws)
                    self.assertEqual(self.w.countries['TUN'].infamy,(10 if tag in ('CPM','CPF') else 15) if province else 0)
    def test_hidden_forms_exclude_each_other_even_after_cooldown(self):
        for _,region,tag in REGIONS[6:]:
            for first,second in [('puppet','province'),('province','puppet')]:
                with self.subTest(tag=tag,first=first):
                    self.w=World(self.scripts);self.w.land(region)
                    self.execute(f'crb_create_{first}_{tag}_effect')
                    subject=self.w.countries[tag]
                    self.w.countries['TUN'].modifiers.discard(COOLDOWN)
                    self.execute(f'crb_create_{second}_{tag}_effect')
                    self.assertIs(self.w.countries[tag],subject)
                    self.assertEqual('crb_province' in subject.variables,first=='province')
                    self.assertNotIn(COOLDOWN,self.w.countries['TUN'].modifiers)
    def test_hidden_names_and_flags_match_form_and_preserve_old_provinces(self):
        names=self.scripts['common/dynamic_country_names/crb_dynamic_country_names.txt']
        flags=self.scripts['common/flag_definitions/crb_hidden_province_flags.txt']
        for _,region,tag in REGIONS[6:]:
            for form in ('puppet','province'):
                with self.subTest(tag=tag,form=form):
                    self.w=World(self.scripts);self.w.land(region)
                    self.execute(f'crb_create_{form}_{tag}_effect');self.w.saved['actor']=self.w.countries[tag]
                    dynamic=get(get(names,tag),'dynamic_country_name')
                    is_merchant=self.w.conditions(get(dynamic,'trigger'),self.w.ctx())
                    self.assertEqual(is_merchant,form=='puppet')
                    label=self.locales[get(dynamic,'name') if is_merchant else tag]
                    self.assertTrue(label.endswith('商站' if is_merchant else '行省'))
                    candidates=[n.value for n in entries(get(flags,tag),'flag_definition') if self.w.conditions(get(n.value,'trigger',[]),self.w.ctx())]
                    chosen=max(candidates,key=lambda ns:int(get(ns,'priority')))
                    self.assertEqual(get(chosen,'coa'),f'crb_{tag}_trading_post' if is_merchant else f'crb_{tag}')
    def test_foundation_tooltips_have_narrative_outcomes_without_law_lists(self):
        keys=[]
        for path,ns in self.scripts.items():
            if not path.startswith('common/scripted_effects/'):continue
            for n in ns:
                if isinstance(n,Node) and n.key.endswith('_with_tooltip_effect'):
                    visible=[x.value for x in entries(n.value,'custom_tooltip')]
                    if not n.key.startswith('crb_create_'):continue
                    self.assertFalse(any('_law_' in x or '_religion_' in x for x in visible))
                    keys.extend(x for x in visible if x.endswith('_effect_tt') and x!= 'crb_territory_disposition_cooldown_effect_tt')
        for event in EVENTS[6:]:
            for option in entries(self.w.defs[event],'option'):
                keys.extend(n.value for n in walk(option.value) if n.key=='custom_tooltip' and isinstance(n.value,str) and n.value.startswith('crb_create_'))
        self.assertEqual(len(keys),24)
        for key in keys:
            with self.subTest(key=key):
                value=self.locales[key];self.assertNotIn('$law_',value);self.assertNotIn('法律',value)
                self.assertGreater(len(value),30)
    def test_subject_introductions_match_tribute_and_war_rules(self):
        actions=self.scripts['common/diplomatic_actions/crb_subject_actions.txt']
        for kind,percent in [('trading_post',30),('province',50)]:
            intro=self.locales[f'subject_type_crb_{kind}_desc']
            self.assertIn(str(percent)+'%',intro);self.assertIn('参战',intro)
            pact=get(get(actions,'crb_'+kind),'pact')
            self.assertEqual(float(get(pact,'income_transfer')),percent/100)
    def test_starting_interventionism_overrides_the_traditional_template(self):
        setup=get(get(self.scripts['common/history/countries/tun - tunis.txt'],'COUNTRIES'),'c:TUN')
        baseline=next(i for i,n in enumerate(setup) if n.key=='effect_starting_politics_traditional')
        laws=[(i,n.value) for i,n in enumerate(setup) if n.key=='activate_law']
        self.assertIn('law_type:law_interventionism',[law for _,law in laws])
        self.assertNotIn('law_type:law_traditionalism',[law for _,law in laws])
        self.assertTrue(any(i>baseline and law=='law_type:law_interventionism' for i,law in laws))

class EventIncomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def test_all_three_tiers_are_proportional_to_gdp_without_a_flat_minimum(self):
        w=World(self.scripts)
        for tier,ratio in [('very_small',0.000075),('small',0.00015),('medium',0.00025)]:
            for gdp in (0,50_000,2_000_000,100_000_000):
                with self.subTest(tier=tier,gdp=gdp):
                    w.countries['TUN'].gdp=gdp
                    result=w.value(w.defs['crb_event_income_weekly_'+tier],w.ctx())
                    self.assertAlmostEqual(result,gdp*ratio)
    def test_every_positive_event_income_uses_gdp_and_preserves_its_duration(self):
        w=World(self.scripts)
        expected={
            'crb_flavor_tyrian_export_income':('small','60'),
            'crb_flavor_mago_rights_income':('small','60'),
            'crb_flavor_shipwreck_rights_income':('medium','60'),
            'crb_flavor_privateering_income':('medium','36'),
            'crb_flavor_coin_melting_income':('very_small','36'),
        }
        positive={key for key,nodes in w.defs.items() if isinstance(nodes,list) and get(nodes,'country_tax_income_add')=='1'}
        self.assertEqual(positive,set(expected))
        found={}
        for path,ns in self.scripts.items():
            if not path.startswith('events/'):continue
            for n in walk(ns):
                if n.key=='add_modifier' and get(n.value,'name') in positive:
                    name=get(n.value,'name');tier,months=expected[name]
                    self.assertEqual(get(n.value,'multiplier'),'crb_event_income_weekly_'+tier)
                    self.assertEqual(get(n.value,'months'),months)
                    found[name]=True
                elif n.key=='add_treasury':
                    # The sole treasury payment is the existing negative veteran bounty.
                    self.assertIn('crb_hb_veterans_bounty_cost',str(n.value))
        self.assertEqual(set(found),positive)

if __name__=='__main__':unittest.main()
