"""Lebanon-only resource potential, migration safety, and company compatibility.

These interpret the authored scripts, not the game's construction-cap engine.
"""
import unittest
from test_territories import World,get,load_scripts
from test_gaul_and_governance import walk

BUILDING='building_crb_lebanon_dye_plantation'
GROUP='bg_crb_lebanon_dye_plantations'
EFFECT='crb_initialize_lebanon_dye_capacity_effect'
MONTHLY='crb_initialize_lebanon_dyes_on_monthly_pulse'

class LebanonDyeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def setUp(self):
        self.w=World(self.scripts);self.w.country('EGY')
        self.state=self.w.land('STATE_LEBANON','EGY')
        self.ctx=self.w.ctx()
        self.region=self.w.resolve('s:STATE_LEBANON',self.ctx)
        # Vanilla 1.15 baseline: 30 arable land and these three resources.
        self.region.arable_land=30
        self.region.resource_potential.update(bg_coal_mining=44,bg_logging=4,bg_fishing=5)
    def monthly(self,owner):
        ctx=self.w.ctx(owner);action=self.w.defs[MONTHLY]
        if self.w.conditions(get(action,'trigger'),ctx):self.w.effect(get(action,'effect'),ctx)
    def test_new_campaign_adds_only_fifteen_dye_potential_regardless_of_owner(self):
        action=self.w.defs['crb_initialize_lebanon_dyes_on_start']
        self.w.effect(get(action,'effect'),self.ctx)
        self.assertEqual(self.region.resource_potential,{
            'bg_coal_mining':44,'bg_logging':4,'bg_fishing':5,GROUP:15})
        self.assertEqual(self.region.arable_land,30)
        self.assertEqual(self.state.buildings,{})
        self.assertFalse(self.w.countries['TUN'].variables)
        tunisia=self.w.resolve('s:STATE_TUNISIA',self.ctx)
        self.assertFalse(tunisia.resource_potential)
    def test_old_save_monthly_backfill_split_ownership_and_transfer_do_not_stack(self):
        # This save predates the new game callback. The actual owner fills it in.
        self.monthly('TUN');self.assertNotIn(GROUP,self.region.resource_potential)
        self.monthly('EGY');self.assertEqual(self.region.resource_potential[GROUP],15)
        self.w.land('STATE_LEBANON','TUN')
        for _ in range(12):self.monthly('EGY');self.monthly('TUN')
        self.state.owner='TUN';self.monthly('TUN')
        self.w.effect(self.w.defs[EFFECT],self.ctx)
        self.assertEqual(self.region.resource_potential[GROUP],15)
        self.assertEqual(self.region.arable_land,30)
        self.assertIn('crb_lebanon_dye_capacity_initialized',self.region.variables)
    def test_only_the_new_regional_plantation_has_the_resource_cap(self):
        building=self.w.defs[BUILDING];group=self.w.defs[GROUP]
        self.assertEqual(get(building,'building_group'),GROUP)
        self.assertEqual(get(group,'parent_group'),'bg_dye_plantations')
        self.assertEqual(get(group,'default_building'),BUILDING)
        self.assertEqual(get(group,'capped_by_resources'),'yes')
        self.assertEqual(get(group,'depletable_resource'),'no')
        self.assertTrue(self.w.conditions(get(building,'potential'),self.ctx.enter(self.state)))
        for name in ('STATE_SYRIA','STATE_ALEPPO','STATE_TUNISIA'):
            state=self.w.land(name)
            self.assertFalse(self.w.conditions(get(building,'potential'),self.ctx.enter(state)))
        # Global vanilla buildings/groups are referenced rather than replaced.
        self.assertNotIn('building_dye_plantation',self.w.defs)
        self.assertNotIn('bg_dye_plantations',self.w.defs)
        self.assertFalse([n for n in walk(self.w.defs[EFFECT]) if n.key in ('add_arable_land','create_building')])
        hooks=self.scripts['common/on_actions/crb_resource_on_actions.txt']
        self.assertIn('crb_initialize_lebanon_dyes_on_start',get(get(hooks,'on_game_started'),'on_actions'))
        self.assertIn(MONTHLY,get(get(hooks,'on_monthly_pulse_country'),'on_actions'))
    def test_tyrian_company_and_dye_event_apply_to_the_regional_building(self):
        company=self.w.defs['company_crb_tyrian_purple']
        self.assertIn(BUILDING,get(company,'building_types'))
        eligible={n.value for n in walk(get(company,'possible')) if n.key=='is_building_type'}
        self.assertIn(BUILDING,eligible)
        self.assertIn('building_dye_plantation',eligible)
        for modifiers in (get(company,'prosperity_modifier'),self.w.defs['crb_flavor_tyrian_purple']):
            self.assertEqual(get(modifiers,BUILDING+'_throughput_add'),
                             get(modifiers,'building_dye_plantation_throughput_add'))
        self.assertEqual(get(company,'possible_prestige_goods'),['prestige_good_crb_tyrian_purple'])
        self.assertEqual(get(self.w.defs['prestige_good_crb_tyrian_purple'],'base_good'),'dye')

if __name__=='__main__':unittest.main()
