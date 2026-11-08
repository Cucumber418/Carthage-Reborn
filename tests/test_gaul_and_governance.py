"""Actual-script regressions; timing, UI and succession still need the game."""
from pathlib import Path
import json
import struct
import unittest
from test_territories import Node,World,entries,get,load_scripts,parse
from test_localization import load_chinese

ROOT=Path(__file__).resolve().parents[1]
POLICIES=('crb_gallic_appeasement','crb_flavor_gallic_legacy','crb_gallic_nonintervention')
def payload(option):
    return [n for n in option if n.key not in ('name','trigger','show_as_unavailable','default_option','ai_chance')]
def walk(nodes):
    for n in nodes:
        if isinstance(n,Node):
            yield n
            if isinstance(n.value,list):yield from walk(n.value)

class GallicCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def setUp(self):
        self.w=World(self.scripts);self.w.country('FRA',gdp=80_000_000)
        home=self.w.land('STATE_CONSTANTINE');self.french=self.w.land('STATE_ALGIERS','FRA')
        self.w.borders=[(home,self.french,True)]
    def execute(self,key):self.w.effect(self.w.defs[key],self.w.ctx())
    def choose(self,suffix):
        option=next(n.value for n in entries(self.w.defs['crb_flavor.17'],'option') if get(n.value,'name')=='crb_flavor.17.'+suffix)
        self.w.effect(payload(option),self.w.ctx());return option
    def test_three_visible_choices_default_to_neutral(self):
        event=self.w.defs['crb_flavor.17'];options=entries(event,'option')
        self.assertEqual(len(options),3);self.assertIsNone(get(event,'fire_only_once'))
        self.assertEqual([get(o.value,'name') for o in options if get(o.value,'default_option')=='yes'],['crb_flavor.17.c'])
        self.w.countries['TUN'].diplomatic_enemies.add('FRA')
        first=options[0].value
        self.assertFalse(self.w.conditions(get(first,'trigger'),self.w.ctx()))
        self.assertTrue(self.w.conditions(get(first,'show_as_unavailable'),self.w.ctx()))
        self.assertTrue(self.w.conditions(get(options[1].value,'trigger'),self.w.ctx()))
    def test_gift_transfers_exactly_one_percent_of_payers_gdp_and_truce_is_bilateral(self):
        tun=self.w.countries['TUN'];fra=self.w.countries['FRA'];tun.gdp=2_000_000;tun.treasury=100_000;fra.treasury=500_000
        self.execute('crb_check_french_border_effect');self.choose('a')
        self.assertEqual((tun.treasury,fra.treasury),(80_000,520_000))
        self.assertEqual((tun.truces['FRA'],fra.truces['TUN']),(60,60))
        self.assertEqual(tun.relations['FRA'],20)
        self.assertEqual(tun.modifiers.intersection(POLICIES),{'crb_gallic_appeasement'})
    def test_gift_cannot_be_forced_during_hostile_diplomatic_play(self):
        self.w.countries['TUN'].diplomatic_enemies.add('FRA');self.choose('a')
        self.assertFalse(self.w.countries['TUN'].truces)
        self.assertEqual(self.w.countries['TUN'].treasury,0)
        self.assertFalse(self.w.scheduled)
    def test_hostility_reduces_relations_and_retains_ten_percent_kill_bonus(self):
        self.execute('crb_check_french_border_effect');self.choose('b')
        tun=self.w.countries['TUN'];self.assertEqual(tun.relations['FRA'],-50)
        self.assertEqual(tun.modifier_months['crb_flavor_gallic_legacy'],60)
        self.assertEqual(float(get(self.w.defs['crb_flavor_gallic_legacy'],'unit_kill_rate_add')),0.1)
        self.assertFalse(tun.truces);self.assertEqual(tun.treasury,0)
    def test_all_three_choices_schedule_sixty_months_and_do_not_stack(self):
        for suffix,policy in zip('abc',POLICIES):
            with self.subTest(suffix=suffix):
                self.setUp();self.execute('crb_check_french_border_effect');self.choose(suffix)
                tun=self.w.countries['TUN']
                self.assertEqual(tun.modifier_months[policy],60)
                self.assertEqual(self.w.scheduled,[('crb_flavor.17',60,'TUN')])
                self.assertNotIn('crb_gallic_choice_pending',tun.variables)
                before=(tun.treasury,dict(tun.relations));self.choose(suffix)
                self.assertEqual((tun.treasury,tun.relations),before)
                self.assertEqual(len(self.w.scheduled),1)
    def test_neutral_has_no_money_relation_or_combat_reward(self):
        self.execute('crb_check_french_border_effect');self.choose('c');tun=self.w.countries['TUN']
        self.assertEqual(tun.treasury,0);self.assertFalse(tun.relations);self.assertFalse(tun.truces)
        self.assertEqual(tun.modifiers.intersection(POLICIES),{'crb_gallic_nonintervention'})
    def test_expiry_reopens_without_needing_the_border_again(self):
        self.execute('crb_check_french_border_effect');self.choose('b')
        self.w.borders=[];self.execute('crb_check_french_border_effect');self.assertEqual(len(self.w.events),1)
        self.w.effect([Node('remove_modifier','=','crb_flavor_gallic_legacy')],self.w.ctx())
        self.execute('crb_check_french_border_effect');self.execute('crb_check_french_border_effect')
        self.assertEqual(self.w.events,['crb_flavor.17','crb_flavor.17'])
        self.choose('c');self.assertNotIn('crb_flavor_gallic_legacy',self.w.countries['TUN'].modifiers)
    def test_france_exit_cleans_cycle_and_cancels_pending_popup(self):
        self.execute('crb_check_french_border_effect');self.choose('b')
        self.french.owner='TUN';self.execute('crb_check_french_border_effect');tun=self.w.countries['TUN']
        self.assertTrue(tun.modifiers.isdisjoint(POLICIES))
        self.assertTrue(tun.variables.isdisjoint({'crb_gallic_cycle_started','crb_gallic_choice_pending','crb_flavor_17_fired'}))
        self.assertTrue(self.w.conditions(get(self.w.defs['crb_flavor.17'],'cancellation_trigger'),self.w.ctx()))
        count=len(self.w.events);self.execute('crb_check_french_border_effect');self.assertEqual(len(self.w.events),count)
    def test_signed_truce_keeps_its_term_when_france_exits_north_africa(self):
        self.execute('crb_check_french_border_effect');self.choose('a')
        self.french.owner='TUN';self.execute('crb_check_french_border_effect')
        self.assertEqual(self.w.countries['TUN'].truces['FRA'],60)
        self.assertNotIn('crb_gallic_appeasement',self.w.countries['TUN'].modifiers)
    def test_old_save_single_fire_flag_enters_the_new_cycle_after_old_buff_expires(self):
        tun=self.w.countries['TUN'];tun.variables.add('crb_flavor_17_fired');tun.modifiers.add('crb_flavor_gallic_legacy');self.w.borders=[]
        self.execute('crb_check_french_border_effect');self.assertFalse(self.w.events)
        tun.modifiers.remove('crb_flavor_gallic_legacy');self.execute('crb_check_french_border_effect')
        self.assertEqual(self.w.events,['crb_flavor.17'])

class IndividualExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def setUp(self):self.w=World(self.scripts)
    def effect(self,key):self.w.effect(get(self.w.defs[key],'effect'),self.w.ctx())
    def test_all_twenty_four_form_buttons_live_only_in_territorial_journal(self):
        buttons={n.key for n in self.scripts['common/scripted_buttons/crb_expansion_buttons.txt'] if isinstance(n,Node)}
        self.assertEqual(len(buttons),24)
        registered={n.value for n in entries(self.w.defs['je_crb_territories'],'scripted_button')}
        self.assertTrue(buttons<=registered);self.assertEqual(len(registered),36)
        for p,ns in self.scripts.items():
            if p.startswith('common/journal_entries/'):
                for n in ns:
                    if isinstance(n,Node) and n.key!='je_crb_territories':self.assertTrue(buttons.isdisjoint(x.value for x in entries(n.value,'scripted_button')))
    def test_actual_form_gets_one_distinct_button_and_foreign_subject_is_hidden(self):
        for province in (False,True):
            with self.subTest(province=province):
                self.w=World(self.scripts);self.w.countries['TUN'].journals.add('je_crb_territories')
                flags={'crb_carthaginian_subject'}|({'crb_province'} if province else set())
                subject=self.w.country('NUM',overlord='TUN',variables=flags)
                def visible():return [n.key for n in self.scripts['common/scripted_buttons/crb_expansion_buttons.txt'] if isinstance(n,Node) and self.w.conditions(get(n.value,'visible'),self.w.ctx())]
                self.assertEqual(visible(),['crb_expand_NUM_'+('province' if province else 'post')+'_button'])
                self.w.country('FRA');subject.overlord='FRA';self.assertFalse(visible())
    def test_expansion_only_transfers_target_owned_noncapital_land(self):
        self.w.country('NUM',overlord='TUN',variables={'crb_carthaginian_subject'})
        own=self.w.land('STATE_ORAN');foreign=self.w.land('STATE_ORAN','FRA');self.w.country('FRA')
        capital=self.w.land('STATE_CONSTANTINE',capital=True);other=self.w.land('STATE_PROVENCE')
        self.effect('crb_expand_NUM_post_button')
        self.assertEqual((own.owner,foreign.owner,capital.owner,other.owner),('NUM','FRA','TUN','TUN'))
    def test_expansion_revalidates_war_and_overlord_before_handover(self):
        for invalid in ('war','independent','foreign'):
            with self.subTest(invalid=invalid):
                self.w=World(self.scripts);self.w.country('FRA')
                self.w.country('CPF',overlord='TUN',variables={'crb_carthaginian_subject','crb_province'})
                land=self.w.land('STATE_LEBANON')
                if invalid=='war':self.w.countries['TUN'].war=True
                else:self.w.countries['CPF'].overlord='' if invalid=='independent' else 'FRA'
                self.effect('crb_expand_CPF_province_button');self.assertEqual(land.owner,'TUN')

class GovernanceAndRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts();cls.locales=load_chinese()
    def setUp(self):self.w=World(self.scripts)
    def execute(self,key,tag='TUN'):self.w.effect(self.w.defs[key],self.w.ctx(tag))
    def test_both_subject_forms_use_a_monarchy_variant_with_governor_title(self):
        self.assertEqual(get(self.w.defs['law_crb_governor_rule'],'parent'),'law_monarchy')
        for form in ('puppet','province'):
            with self.subTest(form=form):
                self.w=World(self.scripts);self.w.land('STATE_LEBANON');self.execute(f'crb_create_{form}_CPF_effect')
                subject=self.w.countries['CPF'];self.assertIn('law_type:law_crb_governor_rule',subject.laws)
                self.assertIn('crb_governor_rule_initialized',subject.variables)
                gov=self.w.defs['gov_crb_'+('province' if form=='province' else 'trading_post')+'_governor']
                self.assertTrue(self.w.conditions(get(gov,'possible'),self.w.ctx('CPF')))
                self.assertEqual(get(gov,'transfer_of_power'),'dictatorial')
                self.assertEqual(get(gov,'male_ruler'),'"RULER_TITLE_CRB_GOVERNOR"')
    def test_old_subject_governance_migrates_once_and_never_changes_independent_country(self):
        subject=self.w.country('NUM',overlord='TUN',variables={'crb_carthaginian_subject'})
        effect=get(self.w.defs['crb_monthly_pulse_subject'],'effect')
        self.w.effect(effect,self.w.ctx('NUM'));self.assertIn('law_type:law_crb_governor_rule',subject.laws)
        subject.laws.clear();self.w.effect(effect,self.w.ctx('NUM'));self.assertFalse(subject.laws)
        subject.variables.discard('crb_governor_rule_initialized');subject.overlord=''
        self.w.effect(effect,self.w.ctx('NUM'));self.assertFalse(subject.laws)
    def test_liberty_modifiers_are_small_weekly_additions_and_five_percent_growth_reduction(self):
        protection=self.w.defs['crb_carthaginian_protection'];hegemony=self.w.defs['crb_carthaginian_hegemony']
        self.assertEqual(float(get(protection,'country_liberty_desire_add')),-0.05)
        self.assertEqual(float(get(protection,'country_liberty_desire_increase_mult')),-0.05)
        self.assertEqual(float(get(hegemony,'country_liberty_desire_of_subjects_add')),-0.02)
    def test_starting_migration_controls_override_traditional_template(self):
        setup=get(get(self.scripts['common/history/countries/tun - tunis.txt'],'COUNTRIES'),'c:TUN')
        baseline=next(i for i,n in enumerate(setup) if n.key=='effect_starting_politics_traditional')
        self.assertTrue(any(i>baseline and n.key=='activate_law' and n.value=='law_type:law_migration_controls' for i,n in enumerate(setup)))
    def test_cothon_site_does_not_finish_but_completed_level_does(self):
        state=self.w.states[0];state.buildings['building_crb_cothon']=0
        monthly=get(get(self.w.defs['je_crb_cultural_revival'],'on_monthly_pulse'),'effect')
        harbor=next(n for n in monthly if n.key=='if' and any(x.key=='crb_has_completed_cothon_trigger' for x in walk(get(n.value,'limit'))))
        self.w.effect([harbor],self.w.ctx());self.assertNotIn('crb_revival_harbor_done',self.w.countries['TUN'].variables)
        self.assertNotIn('crb_revival.4',self.w.events)
        state.buildings['building_crb_cothon']=1;self.w.effect([harbor],self.w.ctx())
        self.assertIn('crb_revival_harbor_done',self.w.countries['TUN'].variables)
        self.assertEqual(self.w.events,['crb_revival.4'])
        self.w.effect([harbor],self.w.ctx());self.assertEqual(len(self.w.events),1)
    def test_barca_victory_starts_hannibal_before_colonial_law_and_never_duplicates_it(self):
        tun=self.w.countries['TUN'];tun.variables.add('crb_hanno_barca_concluded')
        self.execute('crb_barca_victory_effect')
        self.assertIn('je_crb_hannibal_returns',tun.journals);self.assertEqual(self.w.events,['crb_hannibal.0'])
        self.w.effect([Node('activate_law','=','law_type:law_colonial_exploitation')],self.w.ctx())
        self.execute('crb_try_start_hannibal_route_effect')
        self.assertEqual(self.w.events,['crb_hannibal.0'])
        self.assertTrue(self.w.conditions(get(self.w.defs['je_crb_hanno_voyage'],'possible'),self.w.ctx()))
    def test_colonial_law_alone_or_hanno_victory_cannot_open_hannibal(self):
        for flags in (set(),{'crb_hanno_victory','crb_hanno_barca_concluded'}):
            with self.subTest(flags=flags):
                self.w=World(self.scripts);tun=self.w.countries['TUN'];tun.variables.update(flags)
                tun.laws.add('law_type:law_colonial_exploitation');self.execute('crb_try_start_hannibal_route_effect')
                self.assertNotIn('crb_hannibal_route_open',tun.variables);self.assertNotIn('je_crb_hannibal_returns',tun.journals)
                self.assertFalse(self.w.conditions(get(self.w.defs['je_crb_hannibal_returns'],'possible'),self.w.ctx()))
                self.assertTrue(self.w.conditions(get(self.w.defs['je_crb_hanno_voyage'],'possible'),self.w.ctx()))
    def test_voyage_uses_the_same_punic_names_as_the_map(self):
        for target,region in [('lixus','FEZ'),('kerne','WEST_SAHARA'),('chretes','SENEGAL'),('chariot','SOUTH_CAMEROON')]:
            text=self.locales[f'crb_hv_{target}_tt'];self.assertIn(f'$STATE_{region}_crb$',text)
            self.assertNotIn('GetStateRegion',text)

class ArtworkIntegrationTests(unittest.TestCase):
    def test_country_panel_subject_pacts_bind_their_own_texture(self):
        actions=parse((ROOT/'common/diplomatic_actions/crb_subject_actions.txt').read_text(encoding='utf-8-sig'))
        subjects=parse((ROOT/'common/subject_types/crb_subject_types.txt').read_text(encoding='utf-8-sig'))
        textures=[]
        for subject in subjects:
            with self.subTest(subject=subject.key):
                action_key=get(subject.value,'diplomatic_action')
                action=get(actions,action_key)
                self.assertEqual(get(get(action,'pact'),'subject_type'),subject.key)
                # Country panels use DiplomaticActionType.GetTexture, independently of texticons.
                texture=get(action,'texture');self.assertIsInstance(texture,str)
                texture=json.loads(texture)
                self.assertTrue((ROOT/texture).is_file())
                self.assertEqual(struct.unpack_from('<II',(ROOT/texture).read_bytes(),12),(256,256))
                textures.append(texture)
        self.assertEqual(len(set(textures)),2)
    def test_companies_use_custom_emblems_and_original_industry_backgrounds(self):
        companies=parse((ROOT/'common/company_types/crb_companies.txt').read_text(encoding='utf-8-sig'))
        backgrounds={
            'company_crb_carthaginian_trade_house':'comp_illu_harbor_shipbuilding.dds',
            'company_crb_tyrian_purple':'comp_illu_manufacturing_light.dds',
            'company_crb_punic_wine':'comp_illu_farm_rice.dds',
            'company_crb_cyprus_copper':'comp_illu_mining.dds',
        }
        self.assertEqual({n.key for n in companies},set(backgrounds))
        for company in companies:
            with self.subTest(company=company.key):
                emblem=json.loads(get(company.value,'icon'))
                self.assertTrue(emblem.startswith('gfx/interface/icons/company_icons/historical_company_icons/crb_'))
                self.assertTrue((ROOT/emblem).is_file())
                self.assertEqual(json.loads(get(company.value,'background')),'gfx/interface/icons/company_icons/company_backgrounds/'+backgrounds[company.key])
    def test_icons_have_valid_dds_mips_and_texticon_registration(self):
        registry=parse((ROOT/'gui/crb_subject_texticons.gui').read_text(encoding='utf-8-sig'))
        self.assertEqual({get(n.value,'icon') for n in entries(registry,'texticon')},{'crb_trading_post','crb_province'})
        for kind in ('trading_post','province'):
            for suffix,size in [('',256),('_15',64)]:
                p=ROOT/f'gfx/interface/icons/diplomatic_action_icons/crb_{kind}{suffix}.dds'
                b=p.read_bytes();self.assertEqual(b[:4],b'DDS ');self.assertEqual(b[84:88],b'DXT5')
                self.assertEqual(struct.unpack_from('<II',b,12),(size,size))
                self.assertEqual(struct.unpack_from('<I',b,28)[0],size.bit_length())
                expected=128;dimension=size
                while True:
                    expected+=max(1,(dimension+3)//4)**2*16
                    if dimension==1:break
                    dimension=max(1,dimension//2)
                self.assertEqual(len(b),expected)
        path=ROOT/'gfx/interface/icons/building_icons/building_crb_cothon.dds'
        self.assertEqual(struct.unpack_from('<II',path.read_bytes(),12),(256,256))
        building=(ROOT/'common/buildings/crb_buildings.txt').read_text(encoding='utf-8-sig')
        self.assertIn('gfx/interface/icons/building_icons/building_crb_cothon.dds',building)

if __name__=='__main__':unittest.main()
