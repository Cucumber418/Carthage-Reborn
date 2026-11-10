"""Real-script regressions for route history and live voyage target references.

The small script interpreter is not Victoria 3's event or GUI engine.
"""
import re
import unittest
from test_territories import Context,Node,World,entries,get,load_scripts
from test_localization import load_localization
from test_gaul_and_governance import payload,walk

JOURNAL='je_crb_hannibal_returns'
INTRO='crb_hannibal.0'
PENDING='crb_hannibal_intro_pending'
TARGETS=(('lixus','FEZ'),('kerne','WEST_SAHARA'),('chretes','SENEGAL'),('chariot','SOUTH_CAMEROON'))

class HannibalReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def setUp(self):
        self.w=World(self.scripts);self.tun=self.w.countries['TUN']
        self.tun.variables.add('crb_hanno_barca_concluded')
    def execute(self,key):self.w.effect(self.w.defs[key],self.w.ctx())
    def enact_colonial_law(self):
        self.w.effect([Node('activate_law','=','law_type:law_colonial_exploitation')],self.w.ctx())
    def accept_intro(self):
        self.w.effect(payload(entries(self.w.defs[INTRO],'option')[0].value),self.w.ctx())
    def test_barca_colonial_law_and_journal_refresh_cannot_repeat_opening(self):
        self.execute('crb_barca_victory_effect');self.accept_intro()
        self.enact_colonial_law()
        voyage='je_crb_hanno_voyage'
        self.assertTrue(self.w.conditions(get(self.w.defs[voyage],'possible'),self.w.ctx()))
        self.w.effect([Node('add_journal_entry','=',[Node('type','=',voyage)])],self.w.ctx())
        for _ in range(12):
            self.w.effect(get(self.w.defs[JOURNAL],'immediate',[]),self.w.ctx())
            self.execute('crb_try_start_hannibal_route_effect')
        self.assertEqual(self.w.events.count(INTRO),1)
        self.assertEqual(self.w.events.count('crb_hanno_voyage.0'),1)
        self.assertEqual(self.tun.infamy,10)
        self.assertTrue(self.w.conditions(get(self.w.defs[JOURNAL],'possible'),self.w.ctx()))
        # The native manager may auto-activate the JE when route_open changes.
        # The explicit add must recheck presence before adding a second copy.
        class AutoActivatingWorld(World):
            def effect(self,nodes,ctx):
                for node in nodes:
                    super().effect([node],ctx)
                    if node.key=='set_variable' and node.value=='crb_hannibal_route_open':
                        if JOURNAL not in ctx.obj.journals:
                            super().effect([Node('add_journal_entry','=',[Node('type','=',JOURNAL)])],ctx)
        auto=AutoActivatingWorld(self.scripts)
        auto.countries['TUN'].variables.add('crb_hanno_barca_concluded')
        auto.effect(auto.defs['crb_barca_victory_effect'],auto.ctx())
        self.assertEqual(auto.unlocked,1);self.assertEqual(auto.events,[INTRO])
    def test_old_active_journal_without_new_markers_blocks_popup_even_before_backfill(self):
        self.tun.variables.update(('crb_barca_victory','crb_hannibal_route_open'))
        self.tun.journals.add(JOURNAL)
        self.assertFalse(self.w.conditions(get(self.w.defs[INTRO],'trigger'),self.w.ctx()))
        self.enact_colonial_law();self.execute('crb_try_start_hannibal_route_effect')
        self.assertEqual(self.w.events,[])
        self.assertEqual(self.w.unlocked,0)
        self.assertIn('crb_hannibal_intro_shown',self.tun.variables)
        self.assertIn('crb_hannibal_route_started',self.tun.variables)
        self.assertTrue(self.w.conditions(get(self.w.defs[JOURNAL],'possible'),self.w.ctx()))
    def test_old_intro_progress_or_completion_never_reopens_an_inactive_journal(self):
        flags=('crb_hannibal_intro_shown','crb_hannibal_tripoli_done','crb_hannibal_numidia_done',
               'crb_hannibal_syracuse_done','crb_hannibal_islands_done','crb_hannibal_iberia_done',
               'crb_hannibal_new_carthage_done','crb_hannibal_tyre_done','crb_hannibal_concluded')
        for flag in flags:
            with self.subTest(flag=flag):
                self.setUp();self.tun.variables.update(('crb_barca_victory','crb_hannibal_route_open',flag))
                self.enact_colonial_law();self.execute('crb_try_start_hannibal_route_effect')
                self.assertFalse(self.w.events);self.assertNotIn(JOURNAL,self.tun.journals)
                self.assertFalse(self.w.conditions(get(self.w.defs[JOURNAL],'possible'),self.w.ctx()))
                self.assertIn(flag,self.tun.variables)
    def test_event_requires_a_new_opening_request_and_records_its_own_country_history(self):
        self.tun.variables.update(('crb_barca_victory','crb_hannibal_route_open'))
        self.tun.journals.add(JOURNAL)
        trigger=get(self.w.defs[INTRO],'trigger')
        self.assertFalse(self.w.conditions(trigger,self.w.ctx()))
        self.tun.variables.add(PENDING)
        self.assertTrue(self.w.conditions(trigger,self.w.ctx()))
        self.w.effect([Node('trigger_event','=',[Node('id','=',INTRO)])],self.w.ctx())
        self.assertNotIn(PENDING,self.tun.variables)
        self.assertIn('crb_hannibal_intro_shown',self.tun.variables)
        self.assertFalse(self.w.conditions(trigger,self.w.ctx()))
    def test_intro_option_grants_fifteen_claims_and_ten_infamy_only_once(self):
        self.execute('crb_barca_victory_effect');self.accept_intro()
        claims={region:set(countries) for region,countries in self.w.claims.items()}
        self.assertEqual(len(claims),15);self.assertEqual(self.tun.infamy,10)
        self.accept_intro()
        self.assertEqual(self.tun.infamy,10);self.assertEqual(self.w.claims,claims)
    def test_completed_journal_and_legacy_completion_modifier_stay_closed(self):
        self.execute('crb_barca_victory_effect')
        self.tun.variables.update('crb_hannibal_'+name+'_done' for name in ('tripoli','numidia','syracuse','islands','iberia','new_carthage','tyre'))
        outcome=entries(self.w.defs[JOURNAL],'outcome')[0].value
        self.assertTrue(self.w.conditions(get(outcome,'trigger'),self.w.ctx()))
        self.w.effect(get(outcome,'effect'),self.w.ctx());self.tun.journals.discard(JOURNAL)
        self.enact_colonial_law();self.execute('crb_try_start_hannibal_route_effect')
        self.assertEqual(self.w.events,[INTRO,'crb_hannibal.8']);self.assertNotIn(JOURNAL,self.tun.journals)
        self.setUp();self.tun.variables.add('crb_barca_victory');self.tun.modifiers.add('crb_hannibal_returned')
        self.execute('crb_try_start_hannibal_route_effect')
        self.assertIn('crb_hannibal_concluded',self.tun.variables);self.assertFalse(self.w.events)
    def test_only_the_country_route_helper_calls_the_opening_event(self):
        callers=[]
        for path,nodes in self.scripts.items():
            for node in walk(nodes):
                if node.key=='trigger_event' and isinstance(node.value,list) and get(node.value,'id')==INTRO:
                    callers.append(path)
        self.assertEqual(callers,['common/scripted_effects/crb_route_effects.txt'])
        self.assertIsNone(get(self.w.defs[JOURNAL],'immediate'))


class HannoCurrentMapNamesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts=load_scripts()
        cls.locales={lang:load_localization(lang) for lang in ('simp_chinese','english')}
    def setUp(self):
        self.w=World(self.scripts);self.w.country('FRA')
    def refresh(self,ctx=None):
        self.w.effect(self.w.defs['crb_refresh_hanno_target_names_effect'],ctx or self.w.ctx())
    def render_name(self,target,language='simp_chinese'):
        """Resolve the authored Custom branches and State.GetName expressions."""
        fn=self.w.defs['crb_hv_'+target+'_current_name']
        self.assertEqual(get(fn,'type'),'country')
        branch=next(n.value for n in entries(fn,'text') if self.w.conditions(get(n.value,'trigger',[]),self.w.ctx()))
        text=self.locales[language][get(branch,'localization_key')]
        if match:=re.search(r"Var\('([^']+)'\)\.GetState\.GetName",text):
            state=self.w.resolve('var:'+match[1],self.w.ctx())
        else:
            region=re.search(r"GetStateRegion\('([^']+)'\)\.GetLargestStateInRegion\.GetName",text)[1]
            state=max((s for s in self.w.states if s.region==region),key=lambda s:s.area)
        return self.locales[language].get(state.name,state.name)
    def test_foreign_names_are_live_before_any_land_is_acquired(self):
        for target,region in TARGETS:
            state=self.w.land('STATE_'+region,'FRA');state.name='Current '+region;state.area=20
        self.refresh()
        for target,region in TARGETS:
            self.assertEqual(self.render_name(target),'Current '+region)
            state=next(s for s in self.w.states if s.region=='STATE_'+region)
            state.name='Foreign renamed '+region
            self.assertEqual(self.render_name(target),'Foreign renamed '+region)
    def test_our_part_of_a_split_state_and_subsequent_map_renames_take_priority(self):
        for target,region in TARGETS:
            foreign=self.w.land('STATE_'+region,'FRA');foreign.name='Foreign '+region;foreign.area=20
            own=self.w.land('STATE_'+region);own.name='Owned '+region
            self.refresh();self.assertEqual(self.render_name(target),'Owned '+region)
            self.w.effect([Node('set_state_name','=','STATE_'+region+'_crb')],self.w.ctx().enter(own))
            for lang,values in self.locales.items():
                self.assertEqual(self.render_name(target,lang),values['STATE_'+region+'_crb'])
            own.name='Player renamed '+region
            self.assertEqual(self.render_name(target),'Player renamed '+region)
    def test_subject_transfer_and_loss_of_control_refresh_the_state_reference(self):
        foreign=self.w.land('STATE_FEZ','FRA');foreign.name='Foreign Fez';foreign.area=20
        own=self.w.land('STATE_FEZ');own.name='STATE_FEZ_crb'
        self.refresh();self.assertEqual(self.render_name('lixus'),self.locales['simp_chinese']['STATE_FEZ_crb'])
        self.w.country('NUM',overlord='TUN',variables={'crb_carthaginian_subject'});own.owner='NUM'
        self.refresh();self.assertIs(self.w.countries['TUN'].variable_values['crb_hv_lixus_state'],own)
        own.owner='FRA';self.refresh()
        self.assertNotIn('crb_hv_lixus_state',self.w.countries['TUN'].variables)
        self.assertEqual(self.render_name('lixus'),'Foreign Fez')
    def test_deleted_state_reference_falls_back_without_using_an_invalid_state(self):
        foreign=self.w.land('STATE_FEZ','FRA');foreign.name='Fez';foreign.area=20
        own=self.w.land('STATE_FEZ');own.name='STATE_FEZ_crb';self.refresh()
        self.w.states.remove(own)
        self.assertEqual(self.render_name('lixus'),'Fez')
    def test_refresh_handles_state_root_callbacks_and_is_registered_on_all_updates(self):
        own=self.w.land('STATE_FEZ');own.name='STATE_FEZ_crb'
        ctx=Context(self.w.countries['TUN'],root=own)
        self.refresh(ctx)
        self.assertIs(self.w.countries['TUN'].variable_values['crb_hv_lixus_state'],own)
        for key in ('crb_on_state_changed','crb_on_game_started','crb_monthly_pulse_country'):
            self.assertIn('crb_refresh_hanno_target_names_effect',[n.key for n in walk(self.w.defs[key])])
        self.assertIn('crb_refresh_hanno_target_names_effect',[n.key for n in get(self.w.defs['je_crb_hanno_voyage'],'immediate')])

if __name__=='__main__':unittest.main()
