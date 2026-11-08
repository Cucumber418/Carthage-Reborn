"""Validate localization encoding, duplicates and references from actual mod scripts."""
from pathlib import Path
import json
import re
import unittest
from test_territories import Node, get, entries, load_scripts

ROOT=Path(__file__).resolve().parents[1]
ENTRY=re.compile(r'^ ([A-Za-z_0-9.]+):(?:[0-9]+)?\s*(".*")\s*$')

def load_chinese():
    values={};origins={}
    for path in sorted((ROOT/'localization/simp_chinese').rglob('*.yml')):
        data=path.read_bytes()
        if not data.startswith(b'\xef\xbb\xbf'):raise AssertionError('Missing UTF-8 BOM: '+str(path))
        text=data.decode('utf-8-sig')
        if text.splitlines()[0]!='l_simp_chinese:':raise AssertionError('Incorrect language header: '+str(path))
        if '\ufffd' in text or '\ufeff' in text:raise AssertionError('Damaged or extra byte-order mark: '+str(path))
        for number,line in enumerate(text.splitlines()[1:],2):
            if not line.strip() or line.lstrip().startswith('#'):continue
            m=ENTRY.fullmatch(line)
            if not m:raise AssertionError(f'Malformed locale entry: {path}:{number}')
            key=m[1]
            if key in values:raise AssertionError(f'Duplicate {key}: {origins[key]} and {path}')
            values[key]=json.loads(m[2]);origins[key]=path
    return values

def custom_key(value):
    if not isinstance(value,str):return None
    value=value.strip('"')
    return value if re.fullmatch(r'[A-Za-z_0-9.]+',value) and re.search('crb',value,re.I) else None

def ui_references(scripts):
    required={}
    def add(key,path):
        if key:required.setdefault(key,set()).add(path)
    fields={'title','desc','flavor','name','text','custom_tooltip','header','effect_header','conclusion_desc','localization_key','adjective','male_ruler','female_ruler','first_name','last_name','set_interest_group_name','set_state_name'}
    def walk(nodes,path,parent=''):
        for n in nodes:
            if not isinstance(n,Node):continue
            if n.key in fields and not (n.key=='name' and parent in ('set_variable','change_variable','add_progress')):add(custom_key(n.value),path)
            if isinstance(n.value,list):walk(n.value,path,n.key)
    roots={'buildings','cultures','religions','discrimination_traits','discrimination_trait_groups','laws','government_types','ideologies','interest_group_traits','company_types','prestige_goods','production_methods','production_method_groups','static_modifiers','subject_types','diplomatic_actions','journal_entry_groups','journal_entries','game_concepts'}
    for path,nodes in scripts.items():
        walk(nodes,path)
        parts=path.split('/')
        if path.startswith('common/') and parts[1] in roots:
            for n in nodes:
                if isinstance(n,Node) and custom_key(n.key):
                    add(n.key,path)
                    if parts[1]=='journal_entries':add(n.key+'_reason',path)
                    if parts[1]=='game_concepts':add(n.key+'_desc',path)
                    if parts[1]=='subject_types':
                        concept='concept_'+n.key.removeprefix('subject_type_')
                        add(concept,path);add(concept+'_desc',path)
        if path.startswith('common/country_definitions/'):
            for n in nodes:
                if isinstance(n,Node):
                    key=n.key.removeprefix('REPLACE:');add(key,path);add(key+'_ADJ',path)
        if path.startswith('common/cultures/'):
            source=(ROOT/path).read_text(encoding='utf-8-sig')
            for key in re.findall(r'\bcrb_name_[A-Za-z_]+\b',source):add(key,path)
        if path.startswith('common/modifier_type_definitions/'):
            for n in nodes:
                if isinstance(n,Node):add('modifier_'+n.key,path)
    return required

class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.values=load_chinese();cls.scripts=load_scripts()
    def test_core_chinese_was_restored(self):
        for key in ('TUN','crb_carthage','crb_punic','crb_tanit','law_crb_dual_sufetes','RULER_TITLE_CRB_SUFETE','crb_ig_baal_hasadeh','crb_name_Hannibal','je_crb_hanno_barca','crb_carthage.1.t','STATE_TUNISIA_crb'):
            with self.subTest(key=key):self.assertIn(key,self.values)
    def test_custom_ui_references_are_localized(self):
        missing={k:sorted(v) for k,v in ui_references(self.scripts).items() if k not in self.values}
        self.assertFalse(missing,json.dumps(missing,ensure_ascii=False,indent=2))
    def test_all_event_titles_descriptions_and_options_are_localized(self):
        count=0
        for path,nodes in self.scripts.items():
            if not path.startswith('events/'):continue
            for node in nodes:
                if not isinstance(node,Node) or not isinstance(node.value,list) or get(node.value,'type')!='country_event':continue
                count+=1
                keys=[get(node.value,x) for x in ('title','desc','flavor')]
                keys += [get(n.value,'name') for n in entries(node.value,'option')]
                for key in keys:
                    if key:self.assertIn(key.strip('"'),self.values,(path,node.key,key))
        self.assertEqual(count,74)
    def test_custom_dollar_substitutions_are_localized(self):
        missing=set()
        for value in self.values.values():
            for key in re.findall(r'\$([A-Za-z_0-9.]+)(?:\|[^$]*)?\$',value):
                if custom_key(key) and key not in self.values:missing.add(key)
        self.assertFalse(missing,str(sorted(missing)))
    def test_subject_concepts_exist_and_resolve_without_duplicate_text_icons(self):
        concepts={n.key:n.value for path,nodes in self.scripts.items() if path.startswith('common/game_concepts/') for n in nodes if isinstance(n,Node)}
        def expand(key,seen=()):
            self.assertNotIn(key,seen,'Circular localization reference')
            return re.sub(r'\$([A-Za-z_0-9.]+)\$',lambda m:expand(m[1],seen+(key,)),self.values[key])
        for path,nodes in self.scripts.items():
            if not path.startswith('common/subject_types/'):continue
            for n in nodes:
                if not isinstance(n,Node):continue
                concept='concept_'+n.key.removeprefix('subject_type_')
                with self.subTest(subject=n.key):
                    self.assertIn(concept,concepts)
                    name=expand(concept);self.assertRegex(name,r'[\u4e00-\u9fff]')
                    self.assertNotIn('@',name);self.assertNotIn('concept_',name)
                    for key in (n.key,n.key+'_no_icon',get(n.value,'diplomatic_action')):
                        self.assertEqual(expand(key),name)
                    self.assertEqual(expand(concept+'_desc'),expand(n.key+'_desc'))
                    texture=json.loads(get(concepts[concept],'texture'))
                    self.assertTrue((ROOT/texture).is_file())
    def test_border_and_territory_wording_matches_current_rules(self):
        self.assertNotIn('迎面交锋',self.values['crb_flavor.17.d'])
        self.assertIn('非首都',self.values['crb_found_gaul_post_button_desc'])
        self.assertIn('实际附庸',self.values['crb_hannibal_new_carthage_tt'])

if __name__=='__main__':unittest.main()
