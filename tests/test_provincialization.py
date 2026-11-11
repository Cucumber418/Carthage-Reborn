"""Exercise guarded in-place conversion; native effects still require in-game checks."""
import unittest
from test_territories import Node,World,Fleet,entries,get,load_scripts,ECONOMIC_LAWS
from territory_test_data import EUROPE, buttons

REGIONS=[
    ('TRP','TRP',10,'crb_revenge.10'),('NUM','NUM',15,'crb_revenge.11'),
    ('IBT','IBT',15,'crb_revenge.12'),('GLT','GLT',15,'crb_revenge.6'),
    ('SNT','SNT',15,'crb_revenge.7'),('IOP','RPR',15,'crb_revenge.5'),
    ('CPM','CPM',10,'crb_territories.1'),('CPE','CPE',15,'crb_territories.2'),
    ('CPF','CPF',10,'crb_territories.3'),('CPS','CPS',15,'crb_territories.4'),
    ('CPB','CPB',15,'crb_territories.5'),('CPA','CPA',15,'crb_territories.6'),
]
REGIONS.extend((region['tag'], region['tag'], region['infamy'], region['event']) for region in EUROPE)

def walk(nodes):
    for n in nodes:
        if isinstance(n,Node):
            yield n
            if isinstance(n.value,list):yield from walk(n.value)

class ProvincializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scripts=load_scripts()
    def setUp(self):self.w=World(self.scripts)
    def post(self,tag='NUM'):
        self.w.countries['TUN'].journals.add('je_crb_territories')
        return self.w.country(tag,overlord='TUN',pact='crb_trading_post',variables={'crb_carthaginian_subject'})
    def button(self,tag):return self.w.defs[f'crb_provincialize_{tag}_button']
    def visible(self,tag):return self.w.conditions(get(self.button(tag),'visible'),self.w.ctx())
    def possible(self,tag):return self.w.conditions(get(self.button(tag),'possible'),self.w.ctx())
    def convert(self,tag):self.w.effect(get(self.button(tag),'effect'),self.w.ctx())
    def test_all_twelve_buttons_live_only_in_territorial_journal(self):
        keys={n.key for n in buttons(self.scripts, 'crb_provincialize_')}
        self.assertEqual(keys,{f'crb_provincialize_{tag}_button' for tag,*_ in REGIONS})
        for path,nodes in self.scripts.items():
            if not path.startswith('common/journal_entries/'):continue
            for n in nodes:
                if not isinstance(n,Node):continue
                attached={x.value for x in entries(n.value,'scripted_button')}
                self.assertTrue(keys<=attached if n.key=='je_crb_territories' else keys.isdisjoint(attached))
    def test_each_post_converts_without_recreating_country_or_changing_its_assets(self):
        for tag,final,cost,_ in REGIONS:
            with self.subTest(tag=tag):
                self.w=World(self.scripts);post=self.post(tag)
                post.treasury=12345;post.gdp=987654;post.liberty_desire=37.5
                post.modifiers.add('crb_carthaginian_protection');fleet=Fleet(tag);post.fleets.append(fleet)
                post.laws.add('law_type:law_laissez_faire')
                capital=self.w.land('STATE_APULIA',tag,capital=True);capital.buildings['building_port']=4
                home=self.w.states[0];other=self.w.land('STATE_PROVENCE')
                self.w.country('FRA');foreign=self.w.land('STATE_APULIA','FRA')
                count=len(self.w.countries);self.assertTrue(self.visible(tag));self.assertTrue(self.possible(tag))
                self.convert(tag)
                self.assertIs(self.w.countries[final],post);self.assertEqual(len(self.w.countries),count)
                self.assertEqual((post.overlord,post.pact,post.liberty_desire),('TUN','crb_province',37.5))
                self.assertEqual((post.treasury,post.gdp),(12345,987654))
                self.assertEqual((capital.owner,capital.buildings['building_port'],fleet.owner),(final,4,final))
                self.assertEqual((home.owner,other.owner,foreign.owner),('TUN','TUN','FRA'))
                self.assertIn('crb_province',post.variables);self.assertIn('crb_carthaginian_protection',post.modifiers)
                self.assertEqual(post.laws & ECONOMIC_LAWS, {'law_type:law_agrarianism'})
                self.assertTrue({'law_type:law_crb_governor_rule','law_type:law_oligarchy','law_type:law_appointed_bureaucrats','law_type:law_secret_police','law_type:law_mercantilism','law_type:law_state_religion'}<=post.laws)
                self.assertEqual(self.w.countries['TUN'].infamy,cost)
                self.assertEqual(self.w.countries['TUN'].modifier_months['crb_territory_disposition_cooldown'],3)
                self.assertNotIn('crb_territory_disposition_cooldown',post.modifiers)
                self.assertFalse(self.visible(tag))
                expansion=f'crb_expand_{final}_province_button'
                self.assertTrue(self.w.conditions(get(self.w.defs[expansion],'visible'),self.w.ctx()))
    def test_invalid_or_stale_click_never_changes_country_or_charges_infamy(self):
        for reason in ('war','subject_war','cooldown','foreign','independent','indirect','province','unmarked','wrong_type','not_carthage','missing'):
            with self.subTest(reason=reason):
                self.w=World(self.scripts);post=self.post();tun=self.w.countries['TUN']
                self.assertTrue(self.possible('NUM'))
                if reason=='war':tun.war=True
                elif reason=='subject_war':post.war=True
                elif reason=='cooldown':tun.modifiers.add('crb_territory_disposition_cooldown')
                elif reason=='foreign':self.w.country('FRA');post.overlord='FRA'
                elif reason=='independent':post.overlord=''
                elif reason=='indirect':self.w.country('TRP',overlord='TUN');post.overlord='TRP'
                elif reason=='province':post.variables.add('crb_province');post.pact='crb_province'
                elif reason=='unmarked':post.variables.clear()
                elif reason=='wrong_type':post.pact='puppet'
                elif reason=='not_carthage':tun.punic=False
                elif reason=='missing':del self.w.countries['NUM']
                before=(post.pact,set(post.variables),set(post.laws),set(tun.modifiers))
                self.assertFalse(self.possible('NUM'));self.convert('NUM')
                self.assertEqual((post.pact,post.variables,post.laws,tun.modifiers),before)
                self.assertEqual(tun.infamy,0)
    def test_roman_conversion_cannot_overwrite_existing_roman_country(self):
        post=self.post('IOP');self.w.country('FRA')
        rome=self.w.country('RPR',overlord='FRA',treasury=1000)
        land=self.w.land('STATE_LAZIO','RPR')
        self.assertTrue(self.visible('IOP'));self.assertFalse(self.possible('IOP'));self.convert('IOP')
        self.assertIs(self.w.countries['IOP'],post);self.assertIs(self.w.countries['RPR'],rome)
        self.assertEqual((post.pact,rome.overlord,rome.treasury,land.owner),('crb_trading_post','FRA',1000,'RPR'))
        self.assertEqual(self.w.countries['TUN'].infamy,0)
    def test_conversion_shares_cooldown_with_formation_and_cannot_charge_twice(self):
        self.post('NUM');self.post('TRP');tun=self.w.countries['TUN']
        self.convert('NUM');self.assertFalse(self.possible('TRP'));self.convert('TRP')
        self.assertEqual((tun.infamy,self.w.countries['TRP'].pact),(15,'crb_trading_post'))
        self.w.land('STATE_LEBANON')
        self.w.effect(self.w.defs['crb_create_province_CPF_effect'],self.w.ctx())
        self.assertNotIn('CPF',self.w.countries)
        tun.modifiers.clear();self.convert('NUM');self.assertEqual(tun.infamy,15)
        self.convert('TRP');self.assertEqual(tun.infamy,25)
    def test_conversion_infamy_matches_direct_province_foundation(self):
        for tag,_,_,event in REGIONS:
            with self.subTest(tag=tag):
                branch='a' if event.startswith('crb_territories.') else 'b'
                option=next(o.value for o in entries(self.w.defs[event],'option') if get(o.value,'name')==event+'.'+branch)
                cost=next(n.value for n in walk(option) if n.key=='change_infamy')
                call=get(get(self.button(tag),'effect'),'crb_provincialize_territory_effect')
                self.assertEqual(get(call,'INFAMY'),cost)
    def test_old_save_with_only_existing_subjects_unlocks_the_journal_once(self):
        for province in (False,True):
            with self.subTest(province=province):
                self.w=World(self.scripts);post=self.post();tun=self.w.countries['TUN'];tun.journals.clear()
                if province:post.variables.add('crb_province');post.pact='crb_province'
                self.w.land('STATE_CONSTANTINE','NUM')
                self.assertFalse(self.w.conditions(self.w.defs['crb_can_found_any_territory_trigger'],self.w.ctx()))
                for _ in range(2):self.w.effect(self.w.defs['crb_try_unlock_territorial_journal_effect'],self.w.ctx())
                self.assertEqual(tun.journals,{'je_crb_territories'});self.assertEqual(self.w.unlocked,1)

if __name__=='__main__':unittest.main()
