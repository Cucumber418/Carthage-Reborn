"""Check native rank parity and formation gates across both native catalogs."""
from pathlib import Path
import unittest
from test_territories import World,Context,load_scripts,parse,get,entries,Node

class SubjectLimitsTests(unittest.TestCase):
 def test_rank_eligibility_matches_chartered_company(self):
  w=World(load_scripts())
  expected={'minor_power','insignificant_power','unrecognized_regional_power','unrecognized_power'}
  for key in ['subject_type_crb_trading_post','subject_type_crb_province']:
   self.assertEqual(set(get(w.defs[key],'valid_subject_ranks')),expected)
   self.assertEqual(get(w.defs[key],'overlord_must_be_higher_rank'),'no')
   self.assertIn('unrecognized',get(w.defs[key],'valid_overlord_country_types'))
 def test_all_native_formation_paths_block_both_subject_forms_only(self):
  w=World(load_scripts());root=Path(__file__).resolve().parents[1]
  gates=[]
  for file in (root/'common/country_formation').glob('*.txt'):
   for country in parse(file.read_text(encoding='utf-8-sig')):
    for key in ['potential','possible']+(['can_be_formation_candidate'] if get(country.value,'is_major_formation')=='yes' else []):
     nodes=get(country.value,key)
     self.assertIsNotNone(nodes,(country.key,key))
     guards=[n for n in nodes if n.key=='NOT' and entries(n.value,'is_subject_type')]
     self.assertEqual({get(n.value,'is_subject_type') for n in guards},{'subject_type_crb_trading_post','subject_type_crb_province'})
     gates.append(guards)
  self.assertGreater(len(gates),50)
  for pact in ['crb_trading_post','crb_province','puppet','']:
   c=w.country('NUM',overlord='TUN' if pact else '',pact=pact)
   for g in gates:self.assertEqual(w.conditions(g,w.ctx('NUM')),pact not in ['crb_trading_post','crb_province'])
 def test_gaul_split_covers_exactly_the_old_region(self):
  w=World(load_scripts())
  south={'STATE_PROVENCE','STATE_LANGUEDOC','STATE_RHONE','STATE_POITOU','STATE_GUYENNE','STATE_AUVERGNE_LIMOUSIN','STATE_BURGUNDY','STATE_AQUITAINE'}
  north={'STATE_ILE_DE_FRANCE','STATE_NORMANDY','STATE_PICARDY','STATE_ALSACE_LORRAINE','STATE_BRITTANY','STATE_CHAMPAGNE','STATE_FRANCHE_COMTE','STATE_LORRAINE','STATE_ORLEANS','STATE_MAINE_ANJOU','STATE_FRENCH_LOW_COUNTRIES'}
  for state in south|north:
   land=w.land(state)
   self.assertEqual(w.conditions(w.defs['crb_is_gaul_post_state_trigger'],Context(land,root=w.countries['TUN'])),state in south)
   self.assertEqual(w.conditions(w.defs['crb_is_lugdunensis_state_trigger'],Context(land,root=w.countries['TUN'])),state in north)

 def test_legacy_partition_preserves_south_and_excludes_foreign_capital_and_colonies(self):
  for province in [False,True]:
   w=World(load_scripts())
   old=w.country('GLT',overlord='TUN',pact='crb_province' if province else 'crb_trading_post',variables={'crb_carthaginian_subject'} | ({'crb_province'} if province else set()),treasury=5000)
   w.country('FRA')
   south=w.land('STATE_PROVENCE',owner='GLT');north=w.land('STATE_NORMANDY',owner='GLT')
   capital=w.land('STATE_ILE_DE_FRANCE',owner='GLT',capital=True)
   colony=w.land('STATE_PICARDY',owner='GLT',under_colonization=True)
   foreign=w.land('STATE_ORLEANS',owner='FRA')
   w.effect(w.defs['crb_partition_legacy_gaul_effect'],w.ctx())
   self.assertEqual((south.owner,north.owner,capital.owner,colony.owner,foreign.owner),('GLT','XLG','GLT','GLT','FRA'))
   self.assertEqual(old.treasury,5000)
   self.assertEqual('crb_province' in w.countries['XLG'].variables,province)
   self.assertEqual(w.countries['TUN'].infamy,0)
   subject=w.countries['XLG'];w.effect(w.defs['crb_partition_legacy_gaul_effect'],w.ctx());self.assertIs(w.countries['XLG'],subject)
