"""Validate narrative/effect separation and the tooltips used by real choices."""
import re
import unittest
from test_localization import load_localization
from test_territories import Node,entries,get,load_scripts
from territory_test_data import EUROPE, TOTAL_REGIONS, EXPECTED_EVENTS

REGIONS=[
 ('crb_revenge.10','TRP','TRP_crb_province'),
 ('crb_revenge.11','NUM','NUM_crb_province'),
 ('crb_revenge.12','IBT','IBT_crb_province'),
 ('crb_revenge.6','GLT','GLT_crb_province'),
 ('crb_revenge.7','SNT','SNT_crb_province'),
 ('crb_revenge.5','IOP','RPR'),
 *[(f'crb_territories.{i}',tag+'_crb_trading_post',tag) for i,tag in enumerate(('CPM','CPE','CPF','CPS','CPB','CPA'),1)],
]

REGIONS.extend((region['event'], region['tag'] + '_crb_trading_post', region['tag']) for region in EUROPE)

class EventPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scripts=load_scripts()
        cls.defs={n.key:n.value for nodes in cls.scripts.values() for n in nodes if isinstance(n,Node)}
        cls.locales={lang:load_localization(lang) for lang in ('simp_chinese','english')}
    def visible_tooltips(self,nodes):
        for n in nodes:
            if not isinstance(n,Node) or n.key in ('hidden_effect','limit','trigger','ai_chance'):continue
            if n.key=='custom_tooltip' and isinstance(n.value,str):yield n.value
            elif n.key.endswith('_with_tooltip_effect'):yield from self.visible_tooltips(self.defs[n.key])
            elif isinstance(n.value,list):yield from self.visible_tooltips(n.value)
    def test_event_bodies_and_flavor_keep_game_rules_in_the_effect_panel(self):
        count=0
        forbidden=re.compile(r'恶名|解锁|非首都|冷却|\bInfamy\b|\bGDP\b|\bcooldown\b|non-capital|now available for construction',re.I)
        for path,nodes in self.scripts.items():
            if not path.startswith('events/'):continue
            for n in nodes:
                if not isinstance(n,Node) or get(n.value,'type')!='country_event':continue
                count+=1
                for field in ('desc','flavor'):
                    key=get(n.value,field)
                    if not key:continue
                    for lang,values in self.locales.items():
                        with self.subTest(event=n.key,field=field,language=lang):
                            self.assertIsNone(forbidden.search(values[key]),values[key])
        self.assertEqual(count,EXPECTED_EVENTS)
    def test_all_twenty_four_foundations_use_named_concept_links_and_values(self):
        checked=0
        for event,post_name,province_name in REGIONS:
            hidden=event.startswith('crb_territories.')
            for province,name in ((False,post_name),(True,province_name)):
                suffix=('a' if province else 'c') if hidden else ('b' if province else 'a')
                option=next(o.value for o in entries(self.defs[event],'option') if get(o.value,'name')==event+'.'+suffix)
                tooltips=list(self.visible_tooltips(option))
                intros=[k for k in tooltips if k.startswith('crb_create_') and not k.endswith('_effect_tt')]
                details=[k for k in tooltips if k.startswith('crb_create_') and k.endswith('_effect_tt')]
                self.assertEqual(len(intros),1,(event,suffix,tooltips))
                self.assertEqual(len(details),1,(event,suffix,tooltips))
                kind='province' if province else 'trading_post'
                for lang,values in self.locales.items():
                    with self.subTest(event=event,option=suffix,language=lang):
                        intro=values[intros[0]]
                        self.assertIn('#v $'+name+'$#!',intro)
                        self.assertIn('[concept_crb_'+kind+']',intro)
                        self.assertIn('[ROOT.GetCountry.GetName]',intro)
                        self.assertNotIn('@crb_',intro)
                        self.assertIn('#v '+('50%' if province else '30%')+'#!',values[details[0]])
                        self.assertIn('#v 3#!',values['crb_territory_disposition_cooldown_effect_tt'])
                        self.assertNotIn('$law_',values[details[0]])
                checked+=1
        self.assertEqual(checked,TOTAL_REGIONS * 2)
    def test_cothon_unlock_is_explained_in_the_option_tooltip(self):
        event=self.defs['crb_revival.5']
        option=entries(event,'option')[0].value
        self.assertIn('crb_cothon_unlocked_tt',list(self.visible_tooltips(option)))
        for lang,values in self.locales.items():
            with self.subTest(language=lang):
                hint=values['crb_cothon_unlocked_tt']
                self.assertIn('$building_crb_cothon$',hint)
                self.assertIn('$STATE_TUNISIA_crb$',hint)
                self.assertNotIn('$building_crb_cothon$',values[get(event,'desc')])

if __name__=='__main__':unittest.main()
