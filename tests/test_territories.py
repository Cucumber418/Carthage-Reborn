"""Data regressions for territory scripts; the small interpreter is not a game engine.
Run: python -m unittest discover -s tests -v
"""
from dataclasses import dataclass, field
from pathlib import Path
import json
import math
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\])*"|\?=|>=|<=|!=|[{}=<>]|[^\s{}=<>?\x22#]+')

@dataclass
class Node:
    key: str
    op: str
    value: object

def parse(text):
    tokens = []; end = 0
    for m in TOKEN.finditer(text.lstrip('\ufeff')):
        if m.start() != end:
            raise ValueError('Unrecognized input at '+str(end))
        end = m.end(); t = m.group()
        if not t.isspace() and not t.startswith('#'):
            tokens.append(t)
    if end != len(text.lstrip('\ufeff')):
        raise ValueError('Unrecognized trailing input')
    pos = 0
    def body(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens):
            k = tokens[pos]; pos += 1
            if k == '}':
                if not nested: raise ValueError('Unexpected closing brace')
                return result
            if k == '{': raise ValueError('Unexpected opening brace')
            if pos < len(tokens) and tokens[pos] in ('=', '?=', '>=', '<=', '>', '<', '!='):
                op = tokens[pos]; pos += 1
                if pos >= len(tokens): raise ValueError('Missing value')
                v = tokens[pos]; pos += 1
                if v == '{': v = body(True)
                elif pos < len(tokens) and tokens[pos] == '{':
                    pos += 1; v = Node(v, 'typed', body(True))
                result.append(Node(k, op, v))
            else: result.append(k)
        if nested: raise ValueError('Unclosed block')
        return result
    return body()

def entries(nodes, key): return [n for n in nodes if isinstance(n, Node) and n.key == key]
def get(nodes, key, default=None):
    found = entries(nodes, key)
    if not found: return default
    if len(found) != 1: raise AssertionError('Expected one '+key)
    return found[0].value

def load_scripts():
    result = {}
    for folder in ('common', 'events'):
        for path in sorted((ROOT/folder).rglob('*.txt')):
            result[path.relative_to(ROOT).as_posix()] = parse(path.read_text(encoding='utf-8-sig'))
    return result

def subst(nodes, params):
    def s(v):
        if isinstance(v, str):
            for k, value in params.items(): v = v.replace('$'+k+'$', value)
            return v
        if isinstance(v, list): return [s(x) for x in v]
        if isinstance(v, Node): return Node(s(v.key), v.op, s(v.value))
        return v
    return s(nodes)

@dataclass
class Country:
    tag: str
    punic: bool = False
    war: bool = False
    variables: set = field(default_factory=set)
    modifiers: set = field(default_factory=set)
    journals: set = field(default_factory=set)
    overlord: str = ''
    infamy: int = 0
    religion: str = ''
    laws: set = field(default_factory=set)
    pact: str = ''
    liberty_desire: float = 0
    fleets: list = field(default_factory=list)
    gdp: float = 1_000_000
    treasury: float = 0
    relations: dict = field(default_factory=dict)
    truces: dict = field(default_factory=dict)
    diplomatic_enemies: set = field(default_factory=set)
    modifier_months: dict = field(default_factory=dict)
    modifier_amounts: dict = field(default_factory=dict)
    variable_values: dict = field(default_factory=dict)
    primary_cultures: set = field(default_factory=set)

@dataclass
class State:
    region: str
    owner: str
    capital: bool = False
    buildings: dict = field(default_factory=dict)
    name: str = ''
    area: int = 1
    under_colonization: bool = False

@dataclass
class Fleet:
    owner: str
    ships: list = field(default_factory=list)

@dataclass
class Ship:
    fleet: object

@dataclass
class Region:
    name: str

@dataclass
class Building:
    kind: str
    level: int
    state: object

@dataclass
class Context:
    obj: object
    prev: object = None
    root: object = None
    def enter(self, obj):
        return Context(obj, self, self.root or (obj if isinstance(obj, Country) else None))

class World:
    """Interpret only the PDX subset exercised by these regressions; reject unknowns."""
    def __init__(self, scripts):
        self.scripts = scripts
        self.defs = {n.key:n.value for ns in scripts.values() for n in ns if isinstance(n, Node)}
        self.country_definitions = {
            n.key.removeprefix('REPLACE:'): n.value
            for path, nodes in scripts.items() if path.startswith('common/country_definitions/')
            for n in nodes if isinstance(n, Node)
        }
        self.countries = {'TUN':Country('TUN', punic=True)}
        self.states = [State('STATE_TUNISIA', 'TUN', True)]
        self.borders = []
        self.saved = {}; self.events = []; self.unlocked = 0
        self.scheduled = []
        self.claims = {}
    def ctx(self, tag='TUN'): return Context(self.countries[tag], root=self.countries[tag])
    def country(self, tag, **kw):
        self.countries[tag] = Country(tag, **kw); return self.countries[tag]
    def land(self, region, owner='TUN', capital=False, under_colonization=False):
        s = State(region, owner, capital, under_colonization=under_colonization); self.states.append(s); return s
    def resolve(self, value, ctx):
        if value == 'this': return ctx.obj
        if value == 'root': return ctx.root
        if value == 'prev': return ctx.prev.obj if ctx.prev else None
        if value == 'owner' and isinstance(ctx.obj, State): return self.countries[ctx.obj.owner]
        if value == 'overlord' and isinstance(ctx.obj, Country): return self.countries.get(ctx.obj.overlord)
        if value.startswith('c:'): return self.countries.get(value[2:])
        if value.startswith('s:'): return Region(value[2:])
        if value.startswith('scope:'): return self.saved.get(value[6:])
        if value.startswith('var:'):
            target=getattr(ctx.obj,'variable_values',{}).get(value[4:])
            if isinstance(target,State) and not any(s is target for s in self.states):return None
            return target
        return None
    def items(self, key, ctx):
        o = ctx.obj
        if key.endswith('scope_state'):
            if isinstance(o, Country): return [s for s in self.states if s.owner == o.tag]
            if isinstance(o, Region): return [s for s in self.states if s.region == o.name]
        if key.endswith('subject_or_below'):
            def subordinate(c):
                seen=set(); owner=c.overlord
                while owner and owner not in seen:
                    if owner == o.tag: return True
                    seen.add(owner); owner=self.countries[owner].overlord
                return False
            return [c for c in self.countries.values() if subordinate(c)]
        if key.endswith('scope_building'):
            return [Building(kind,level,s) for s in self.states if s.owner==o.tag for kind,level in s.buildings.items()]
        if key=='any_enemy_in_diplo_play':return [self.countries[tag] for tag in o.diplomatic_enemies if tag in self.countries]
        if key.endswith('military_formation'): return o.fleets
        if key.endswith('scope_ship'):
            return [s for f in o.fleets for s in f.ships] if isinstance(o, Country) else o.ships
        raise AssertionError(('Unknown iterator', key, o))
    @staticmethod
    def compare(a, op, b):
        return {'=':lambda:a==b,'!=':lambda:a!=b,'>':lambda:a>b,'>=':lambda:a>=b,'<':lambda:a<b,'<=':lambda:a<=b}[op]()
    def conditions(self, nodes, ctx): return all(self.condition(n, ctx) for n in nodes)
    def condition(self, n, ctx):
        k, op, v = n.key, n.op, n.value; o = ctx.obj
        if k == 'OR': return any(self.condition(x,ctx) for x in v)
        if k == 'AND': return self.conditions(v,ctx)
        if k == 'NOT': return not self.conditions(v,ctx)
        if k == 'custom_tooltip': return self.conditions([x for x in v if x.key not in ('text','subject')],ctx)
        if k == 'always': return v == 'yes'
        if k == 'exists': return self.resolve(v,ctx) is not None
        if k == 'country_has_primary_culture': return o.punic == (v=='cu:crb_punic')
        if k == 'has_variable': return v in o.variables
        if k == 'has_modifier': return v in o.modifiers
        if k == 'has_journal_entry': return v in o.journals
        if k in ('has_law','has_law_or_variant'): return v in o.laws
        if k == 'is_subject':return bool(o.overlord)==(v=='yes')
        if k == 'is_subject_type':return bool(o.overlord) and get(self.defs[v],'diplomatic_action')==o.pact
        if k in ('this','root') and isinstance(v,str):return self.resolve(k,ctx) is self.resolve(v,ctx)
        if k == 'is_building_type':return o.kind==v
        if k == 'level':return self.compare(o.level,op,float(v))
        if k == 'is_at_war': return o.war == (v=='yes')
        if k == 'is_capital': return o.capital == (v=='yes')
        if k == 'is_under_colonization': return o.under_colonization == (v=='yes')
        if k == 'is_fleet': return isinstance(o,Fleet) == (v=='yes')
        if k == 'has_building': return o.buildings.get(v,0)>0
        if k == 'state_region': return o.region == v.removeprefix('s:')
        if k == 'is_subject_of':
            target=self.resolve(v,ctx);owner=o.overlord
            while owner:
                if target and owner==target.tag:return True
                owner=self.countries[owner].overlord
            return False
        if k == 'is_land_adjacent_to_state':
            target=self.resolve(v,ctx)
            return any(land and ((a is target and b.owner==o.tag) or (b is target and a.owner==o.tag)) for a,b,land in self.borders)
        if k.startswith('any_'):
            candidates=self.items(k,ctx);conditions=[x for x in v if x.key not in ('count','percent')]
            matches=[x for x in candidates if self.conditions(conditions,ctx.enter(x))]
            count=entries(v,'count')
            if count:
                n=count[0]
                return bool(candidates) and len(matches)==len(candidates) if n.value=='all' else self.compare(len(matches),n.op,int(n.value))
            return bool(matches)
        if k in self.defs and k.startswith('crb_'):
            if isinstance(v,list):return self.conditions(subst(self.defs[k],{x.key:x.value for x in v}),ctx)
            if v in ('yes','no'):return self.conditions(self.defs[k],ctx)==(v=='yes')
            return self.compare(self.value(self.defs[k],ctx),op,float(v))
        target=self.resolve(k,ctx)
        if target is None and (k.startswith(('c:','scope:')) or k=='overlord'):return False
        if target is not None:return self.conditions(v,ctx.enter(target))
        raise AssertionError(('Unknown condition',k,v))
    def numeric(self,value,ctx):
        if isinstance(value,list):return self.value(value,ctx)
        if value=='root.gdp':return ctx.root.gdp
        if value in self.defs:return self.value(self.defs[value],ctx)
        return float(value)
    def value(self,nodes,ctx):
        result=0
        for n in nodes:
            if n.key=='value':result=self.numeric(n.value,ctx)
            elif n.key=='add':result+=float(n.value)
            elif n.key=='multiply':result*=float(n.value)
            elif n.key=='divide':result/=float(n.value)
            elif n.key=='round' and n.value=='yes':result=math.floor(result+0.5) if result>=0 else math.ceil(result-0.5)
            elif n.key.startswith('every_'):
                for obj in self.items(n.key,ctx):
                    if self.conditions(get(n.value,'limit',[]),ctx.enter(obj)):
                        result+=self.value([x for x in n.value if x.key!='limit'],ctx.enter(obj))
            else:raise AssertionError(('Unknown value',n))
        return result
    def effect(self,nodes,ctx):
        branch_taken=False
        for n in nodes:
            k,v=n.key,n.value;o=ctx.obj
            if k=='if':
                branch_taken=self.conditions(get(v,'limit'),ctx)
                if branch_taken:self.effect([x for x in v if x.key!='limit'],ctx)
            elif k=='else_if':
                if not branch_taken and self.conditions(get(v,'limit'),ctx):
                    branch_taken=True;self.effect([x for x in v if x.key!='limit'],ctx)
            elif k=='else':
                if not branch_taken:self.effect(v,ctx)
                branch_taken=True
            elif k=='while':
                for _ in range(64):
                    if not self.conditions(get(v,'limit'),ctx):break
                    self.effect([x for x in v if x.key!='limit'],ctx)
                else:raise AssertionError('Nonterminating loop')
            elif k.startswith(('every_','random_')):
                eligible=[x for x in list(self.items(k,ctx)) if self.conditions(get(v,'limit',[]),ctx.enter(x))]
                for obj in eligible[:1] if k.startswith('random_') else eligible:
                    self.effect([x for x in v if x.key!='limit'],ctx.enter(obj))
            elif k=='save_scope_as':self.saved[v]=o
            elif k=='set_variable':
                if isinstance(v,list):
                    name=get(v,'name');value=get(v,'value');o.variables.add(name)
                    target=self.resolve(value,ctx)
                    o.variable_values[name]=target if target is not None else self.numeric(value,ctx)
                else:o.variables.add(v)
            elif k=='remove_variable':o.variables.discard(v);o.variable_values.pop(v,None)
            elif k=='set_state_name':o.name=v
            elif k=='add_claim':self.claims.setdefault(o.name,set()).add(self.resolve(v,ctx).tag)
            elif k=='set_state_religion':o.religion=v
            elif k=='add_primary_culture':
                culture=v.removeprefix('cu:');o.primary_cultures.add(culture)
                if culture=='crb_punic':o.punic=True
            elif k=='add_modifier':
                name=get(v,'name');o.modifiers.add(name)
                if get(v,'months') is not None:o.modifier_months[name]=int(get(v,'months'))
                multiplier=get(v,'multiplier')
                # Only custom script values are modeled; vanilla budgets need the game.
                if multiplier in self.defs:o.modifier_amounts[name]=self.numeric(multiplier,ctx)
            elif k=='remove_modifier':
                o.modifiers.discard(v);o.modifier_months.pop(v,None);o.modifier_amounts.pop(v,None)
            elif k=='add_treasury':o.treasury+=self.numeric(v,ctx)
            elif k=='change_relations':
                target=self.resolve(get(v,'country'),ctx);amount=float(get(v,'value'))
                relation=max(-100,min(100,o.relations.get(target.tag,0)+amount))
                o.relations[target.tag]=relation;target.relations[o.tag]=relation
            elif k=='create_bidirectional_truce':
                target=self.resolve(get(v,'country'),ctx);months=int(get(v,'months'))
                o.truces[target.tag]=months;target.truces[o.tag]=months
            elif k=='activate_law':o.laws.add(v)
            elif k=='change_infamy':o.infamy+=int(v)
            elif k=='create_country':
                tag=get(v,'tag');assert tag not in self.countries
                cultures=set(get(self.country_definitions.get(tag,[]),'cultures',[]))
                country=self.country(tag,primary_cultures=cultures,punic='crb_punic' in cultures)
                state=self.resolve(get(v,'state'),ctx)
                state.owner=tag
                self.effect(get(v,'on_created'),ctx.enter(country))
            elif k=='set_state_owner':o.owner=self.resolve(v,ctx).tag
            elif k=='create_diplomatic_pact':
                subject=self.resolve(get(v,'country'),ctx);subject.overlord=o.tag;subject.pact=get(v,'type')
            elif k=='change_subject_type':
                assert o.overlord
                o.pact=get(self.defs[v],'diplomatic_action')
            elif k=='change_tag':
                assert v not in self.countries
                old=o.tag;del self.countries[old];o.tag=v;self.countries[v]=o
                for state in self.states:
                    if state.owner==old:state.owner=v
                for country in self.countries.values():
                    if country.overlord==old:country.overlord=v
                    for fleet in country.fleets:
                        if fleet.owner==old:fleet.owner=v
            elif k=='create_military_formation':
                fleet=Fleet(o.tag);o.fleets.append(fleet)
            elif k=='create_ship':
                fleet=self.resolve(get(v,'fleet'),ctx);fleet.ships.append(Ship(fleet))
            elif k=='kill_ship':o.fleet.ships.remove(o)
            elif k=='create_building':o.buildings[get(v,'building')]=max(o.buildings.get(get(v,'building'),0),int(get(v,'level','1')))
            elif k=='add_journal_entry':
                key=get(v,'type');assert key not in o.journals
                self.conditions(get(self.defs[key],'possible'),ctx) or self.fail('Invalid journal')
                o.journals.add(key);self.unlocked+=1;self.effect(get(self.defs[key],'immediate',[]),ctx)
            elif k=='trigger_event':
                key=get(v,'id');ev=self.defs[key]
                if get(v,'months') is not None:
                    self.scheduled.append((key,int(get(v,'months')),o.tag));continue
                if self.conditions(get(ev,'trigger',[]),ctx):
                    self.events.append(key);self.effect(get(ev,'immediate',[]),ctx)
            elif k=='hidden_effect':self.effect(v,ctx)
            elif k=='custom_tooltip' and isinstance(v,list):
                self.effect([x for x in v if x.key not in ('text','subject')],ctx)
            elif k in ('custom_tooltip','show_as_tooltip'):continue
            elif k=='crb_apply_punic_state_names_effect':continue # cosmetic subsystem outside this harness
            elif k in self.defs and k.startswith('crb_'):
                self.effect(subst(self.defs[k],{x.key:x.value for x in v}) if isinstance(v,list) else self.defs[k],ctx)
            else:
                target=self.resolve(k,ctx)
                if target is None and n.op=='?=':continue
                if target is None:raise AssertionError(('Unknown effect',k,v))
                self.effect(v,ctx.enter(target))
    @staticmethod
    def fail(message):raise AssertionError(message)

class TerritoriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.scripts=load_scripts()
    def setUp(self): self.w=World(self.scripts)
    def check(self,key):return self.w.conditions(self.w.defs[key],self.w.ctx())
    def execute(self,key):self.w.effect(self.w.defs[key],self.w.ctx())
    def button(self,key):
        b=self.w.defs[key];return self.w.conditions(get(b,'visible'),self.w.ctx()) and self.w.conditions(get(b,'possible'),self.w.ctx())
    def unlock(self):self.execute('crb_try_unlock_territorial_journal_effect')
    def test_start_has_no_territorial_journal(self):
        self.unlock();self.assertFalse(self.w.countries['TUN'].journals)
    def test_one_constantine_is_enough_and_journal_opens_once(self):
        self.w.land('STATE_CONSTANTINE');self.unlock();self.unlock()
        self.assertTrue(self.button('crb_found_numidia_post_button'));self.assertEqual(self.w.unlocked,1)
    def test_one_gaul_state_needs_no_revenge_progress(self):
        self.w.land('STATE_PROVENCE');self.unlock()
        self.assertTrue(self.button('crb_found_gaul_post_button'))
        self.assertNotIn('crb_revenge_stage2_taken',self.w.countries['TUN'].variables)
    def test_war_waits_to_unlock_and_disables_establishment(self):
        self.w.land('STATE_PROVENCE');self.w.countries['TUN'].war=True;self.unlock()
        self.assertFalse(self.w.countries['TUN'].journals)
        self.w.countries['TUN'].war=False;self.unlock();self.w.countries['TUN'].war=True
        self.assertFalse(self.button('crb_found_gaul_post_button'))
    def test_only_capital_in_region_is_not_disposable(self):
        self.w.states[0].capital=False;self.w.land('STATE_PROVENCE',capital=True);self.unlock()
        self.assertFalse(self.check('crb_can_found_gaul_trigger'))
    def test_existing_or_foreign_tag_is_not_overwritten(self):
        self.w.land('STATE_CONSTANTINE');self.w.country('NUM');self.execute('crb_create_puppet_NUM_effect')
        self.assertEqual(self.w.states[-1].owner,'TUN');self.assertFalse(self.w.countries['NUM'].overlord)
    def test_subject_creation_transfers_only_owned_eligible_noncapital_states(self):
        own=self.w.land('STATE_CONSTANTINE');foreign=self.w.land('STATE_ALGIERS','FRA');self.w.country('FRA')
        self.execute('crb_create_province_NUM_effect');subject=self.w.countries['NUM']
        self.assertEqual((own.owner,foreign.owner,self.w.states[0].owner),('NUM','FRA','TUN'))
        self.assertEqual((subject.overlord,subject.pact,subject.religion),('TUN','crb_province','rel:crb_tanit'))
        self.assertIn('crb_province',subject.variables)
        self.assertIn('law_type:law_oligarchy',subject.laws)
        self.execute('crb_create_province_NUM_effect');self.assertEqual(len(self.w.countries),3)
    def test_merchant_and_province_have_different_laws(self):
        self.w.land('STATE_PROVENCE');self.execute('crb_create_puppet_GLT_effect')
        subject=self.w.countries['GLT'];self.assertNotIn('crb_province',subject.variables)
        self.assertEqual(subject.pact,'crb_trading_post');self.assertIn('law_type:law_landed_voting',subject.laws)
    def test_journal_remains_available_after_land_transfer(self):
        self.w.land('STATE_CONSTANTINE');self.unlock();self.execute('crb_create_puppet_NUM_effect')
        self.assertTrue(self.w.conditions(get(self.w.defs['je_crb_territories'],'possible'),self.w.ctx()))
        self.assertTrue(self.check('crb_initial_conquests_trigger'))
    def test_hidden_regions_only_reveal_their_own_button(self):
        self.w.land('STATE_LEBANON');self.unlock()
        self.assertTrue(self.button('crb_found_phoenicia_province_button'))
        self.assertFalse(self.button('crb_found_egypt_province_button'))
    def test_hidden_province_can_be_created_from_one_inland_state(self):
        s=self.w.land('STATE_BAGHDAD');self.execute('crb_create_province_CPB_effect')
        self.assertEqual(s.owner,'CPB');self.assertEqual(self.w.countries['CPB'].overlord,'TUN')
    def test_roman_options_exclude_each_other(self):
        self.w.land('STATE_APULIA');self.execute('crb_create_puppet_IOP_effect')
        self.w.countries['TUN'].modifiers.discard('crb_territory_disposition_cooldown')
        self.execute('crb_create_puppet_RPR_effect')
        self.assertIn('IOP',self.w.countries);self.assertNotIn('RPR',self.w.countries)
    def test_pending_province_option_does_not_charge_if_war_starts(self):
        self.w.land('STATE_CONSTANTINE');self.w.countries['TUN'].war=True
        option=[o.value for o in entries(self.w.defs['crb_revenge.11'],'option') if get(o.value,'name')=='crb_revenge.11.b'][0]
        self.w.effect([n for n in option if n.key not in ('name','trigger','default_option')],self.w.ctx())
        self.assertEqual(self.w.countries['TUN'].infamy,0);self.assertNotIn('NUM',self.w.countries)
    def test_pending_province_option_does_not_charge_after_land_loss(self):
        self.w.country('FRA');self.w.land('STATE_CONSTANTINE','FRA')
        option=[o.value for o in entries(self.w.defs['crb_revenge.11'],'option') if get(o.value,'name')=='crb_revenge.11.b'][0]
        self.w.effect([n for n in option if n.key not in ('name','trigger','default_option')],self.w.ctx())
        self.assertEqual(self.w.countries['TUN'].infamy,0);self.assertNotIn('NUM',self.w.countries)
    def test_border_event_needs_land_border_in_french_north_africa(self):
        self.w.country('FRA');home=self.w.land('STATE_CONSTANTINE');france=self.w.land('STATE_ALGIERS','FRA')
        self.w.borders=[(home,france,False)];self.execute('crb_check_french_border_effect');self.assertFalse(self.w.events)
        self.w.borders=[(home,france,True)];self.execute('crb_check_french_border_effect');self.execute('crb_check_french_border_effect')
        self.assertEqual(self.w.events,['crb_flavor.17'])
    def test_european_french_border_does_not_trigger(self):
        self.w.country('FRA');home=self.w.land('STATE_PROVENCE');france=self.w.land('STATE_RHONE','FRA')
        self.w.borders=[(home,france,True)];self.execute('crb_check_french_border_effect');self.assertFalse(self.w.events)
    def test_french_border_without_france_is_safe(self):
        self.execute('crb_check_french_border_effect');self.assertFalse(self.w.events)
    def test_split_iberian_holdings_are_aggregated(self):
        self.w.land('STATE_CATALONIA');self.w.country('IBT',overlord='TUN',variables={'crb_carthaginian_subject'})
        self.w.land('STATE_MURCIA','IBT');self.w.land('STATE_VALENCIA','IBT')
        self.assertEqual(self.w.value(self.w.defs['crb_controlled_iberian_states'],self.w.ctx()),3)
        self.w.countries['IBT'].overlord='';self.assertEqual(self.w.value(self.w.defs['crb_controlled_iberian_states'],self.w.ctx()),1)
    def test_starting_navy_is_exactly_three_with_or_without_original_fleet(self):
        setup=self.scripts['common/history/military_formations/zz_crb_starting_navy.txt']
        for original in (0,1,3,5):
            with self.subTest(original=original):
                self.w=World(self.scripts);c=self.w.countries['TUN']
                if original:
                    f=Fleet('TUN');f.ships=[Ship(f) for _ in range(original)];c.fleets=[f]
                self.w.effect(get(setup,'MILITARY_FORMATIONS'),self.w.ctx())
                self.assertEqual(sum(len(f.ships) for f in c.fleets),3)
    def test_naval_administration_does_not_duplicate_vanilla_level(self):
        data=self.scripts['common/history/buildings/zz_crb_naval_administration.txt']
        state_nodes=get(get(get(data,'BUILDINGS'),'s:STATE_TUNISIA'),'region_state:TUN')
        for original in (0,1):
            with self.subTest(original=original):
                s=self.w.states[0];s.buildings={'building_naval_administration':original}
                self.w.effect(state_nodes,self.w.ctx().enter(s));self.assertEqual(s.buildings['building_naval_administration'],1)
    def test_establishment_buttons_only_belong_to_territorial_journal(self):
        journal=self.w.defs['je_crb_territories']
        buttons={n.key for n in self.scripts['common/scripted_buttons/crb_territory_buttons.txt'] if isinstance(n,Node)}
        self.assertEqual(len(buttons),12)
        self.assertTrue(buttons.issubset({n.value for n in entries(journal,'scripted_button')}))
        for path,ns in self.scripts.items():
            if not path.startswith('common/journal_entries/'):continue
            for n in ns:
                if isinstance(n,Node) and n.key!='je_crb_territories':
                    self.assertTrue(buttons.isdisjoint(x.value for x in entries(n.value,'scripted_button')))
        self.assertNotRegex((ROOT/'events/crb_hannibal_events.txt').read_text(encoding='utf-8-sig'),r'crb_create_(puppet|province)_')
    def test_expansion_supports_early_numidia_and_protects_foreign_subject_tags(self):
        self.w.land('STATE_CONSTANTINE');self.unlock();self.execute('crb_create_puppet_NUM_effect')
        extra=self.w.land('STATE_ALGIERS');foreign=self.w.land('STATE_PROVENCE')
        self.w.country('FRA');self.w.country('GLT',overlord='FRA',variables={'crb_carthaginian_subject'})
        self.execute('crb_expand_trading_posts_effect')
        self.assertEqual(extra.owner,'NUM');self.assertEqual(foreign.owner,'TUN')
        decision=self.w.defs['crb_expand_trading_posts_decision']
        self.assertTrue(self.w.conditions(get(decision,'is_shown'),self.w.ctx()))
    def test_split_state_foreign_part_is_never_transferred(self):
        own=self.w.land('STATE_CONSTANTINE');foreign=self.w.land('STATE_CONSTANTINE','FRA');self.w.country('FRA')
        self.execute('crb_create_puppet_NUM_effect')
        self.assertEqual((own.owner,foreign.owner),('NUM','FRA'))
    def test_all_six_hidden_provinces_form_from_one_state(self):
        for region,tag in [('STATE_FEZ','CPM'),('STATE_MIDDLE_EGYPT','CPE'),('STATE_LEBANON','CPF'),('STATE_ALEPPO','CPS'),('STATE_MOSUL','CPB'),('STATE_YEMEN','CPA')]:
            with self.subTest(region=region):
                self.w=World(self.scripts);s=self.w.land(region);self.unlock()
                self.execute('crb_create_province_'+tag+'_effect')
                self.assertEqual(s.owner,tag);self.assertEqual(self.w.countries[tag].pact,'crb_province')
    def test_old_subject_that_became_independent_does_not_count_as_controlled(self):
        self.w.country('NUM',variables={'crb_carthaginian_subject'})
        self.w.land('STATE_CONSTANTINE','NUM')
        self.assertFalse(self.w.conditions(subst(self.w.defs['crb_controls_region_trigger'],{'REGION':'STATE_CONSTANTINE'}),self.w.ctx()))
        self.w.countries['NUM'].overlord='TUN'
        self.assertTrue(self.w.conditions(subst(self.w.defs['crb_controls_region_trigger'],{'REGION':'STATE_CONSTANTINE'}),self.w.ctx()))
    def test_art_textures_have_expected_dds_headers_and_dimensions(self):
        paths=[]
        for folder in ('company_types','prestige_goods'):
            for file in (ROOT/'common'/folder).glob('*.txt'):
                paths+=re.findall(r'(?:icon|background|texture) = "(gfx/[^\"]*crb_[^\"]+\.dds)"',file.read_text(encoding='utf-8-sig'))
        self.assertEqual(len(paths),1)
        for rel in paths:
            with self.subTest(texture=rel):
                b=(ROOT/rel).read_bytes();self.assertEqual(b[:4],b'DDS ')
                height,width=struct.unpack_from('<II',b,12)
                self.assertEqual((width,height),(512,256) if '/company_backgrounds/' in rel else (256,256))
                self.assertEqual(b[84:88],b'DXT5')
    def test_territorial_ui_keys_and_tooltips_have_chinese_text(self):
        texts={}
        for p in (ROOT/'localization/simp_chinese').glob('*.yml'):
            data=p.read_bytes();self.assertTrue(data.startswith(b'\xef\xbb\xbf'))
            for k,v in re.findall(r'^ (\S+):\s*(".*")$',data.decode('utf-8-sig'),re.M):
                self.assertNotIn(k,texts);texts[k]=json.loads(v)
        for path in ('common/scripted_buttons/crb_territory_buttons.txt','events/crb_territories_events.txt'):
            source=(ROOT/path).read_text(encoding='utf-8-sig')
            for key in re.findall(r'(?:name|desc|title|flavor)\s*=\s*(crb_[\w.]+)',source):self.assertIn(key,texts)
        for key in re.findall(r'custom_tooltip\s*=\s*(crb_create_\w+)',(ROOT/'common/scripted_effects/crb_effects.txt').read_text(encoding='utf-8-sig')):self.assertIn(key,texts)

if __name__=='__main__':unittest.main()
