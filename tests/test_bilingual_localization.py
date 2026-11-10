"""Check the English language layer against Chinese and the actual UI references."""
from collections import Counter
import re
import unittest
from test_localization import ROOT,ENTRY,custom_key,load_localization,ui_references
from test_territories import load_scripts

PROTECTED=re.compile(r'\[[^\]]*\]|\$[^$\n]+\$|@[A-Za-z0-9_]+!')
FORMATTING=re.compile(r'#[A-Za-z_]+|#!')
DOLLAR=re.compile(r'\$([A-Za-z_0-9.]+)(?:\|[^$]*)?\$')

class BilingualLocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zh=load_localization('simp_chinese')
        cls.en=load_localization('english')
        cls.scripts=load_scripts()
    def test_matching_language_files_including_replace_overrides(self):
        root=ROOT/'localization'
        expected={str(p.relative_to(root/'simp_chinese')).replace('_l_simp_chinese.yml','_l_english.yml') for p in (root/'simp_chinese').rglob('*.yml')}
        actual={str(p.relative_to(root/'english')) for p in (root/'english').rglob('*.yml')}
        self.assertEqual(actual,expected)
        for rel in expected:
            with self.subTest(file=rel):
                en_path=root/'english'/rel
                zh_path=root/'simp_chinese'/rel.replace('_l_english.yml','_l_simp_chinese.yml')
                def keys(path):
                    return {m[1] for line in path.read_text(encoding='utf-8-sig').splitlines() if (m:=ENTRY.fullmatch(line))}
                self.assertEqual(keys(en_path),keys(zh_path))
    def test_english_and_chinese_have_the_same_key_set(self):
        self.assertTrue(self.zh)
        self.assertEqual(set(self.en),set(self.zh))
    def test_english_covers_every_custom_ui_reference(self):
        self.assertFalse({k:sorted(v) for k,v in ui_references(self.scripts).items() if k not in self.en})
    def test_runtime_expressions_substitutions_and_icons_are_preserved(self):
        for key,zh in self.zh.items():
            with self.subTest(key=key):
                self.assertEqual(Counter(PROTECTED.findall(zh)),Counter(PROTECTED.findall(self.en[key])))
    def test_formatting_and_paragraph_breaks_are_preserved(self):
        for key,zh in self.zh.items():
            with self.subTest(key=key):
                en=self.en[key]
                self.assertEqual(Counter(FORMATTING.findall(zh)),Counter(FORMATTING.findall(en)))
                self.assertEqual(zh.count('\n'),en.count('\n'))
    def test_visible_numbers_and_percentages_are_preserved(self):
        for key,zh in self.zh.items():
            with self.subTest(key=key):
                def numbers(text):
                    return Counter(re.findall(r'\d+(?:\.\d+)?%?',PROTECTED.sub('',text)))
                self.assertEqual(numbers(zh),numbers(self.en[key]))
    def test_english_custom_substitutions_exist_and_are_acyclic(self):
        complete=set()
        def visit(key,path=()):
            self.assertNotIn(key,path,'Circular substitution: '+' -> '.join(path+(key,)))
            if key in complete:return
            for ref in DOLLAR.findall(self.en[key]):
                if custom_key(ref):self.assertIn(ref,self.en,(key,ref))
                if ref in self.en:visit(ref,path+(key,))
            complete.add(key)
        for key in self.en:visit(key)
    def test_english_contains_no_untranslated_chinese_or_placeholder_text(self):
        for key,value in self.en.items():
            with self.subTest(key=key):
                self.assertNotRegex(value,r'[\u3400-\u9fff\ufffd]')
                self.assertNotRegex(value,r'\b(?:TODO|TBD|TRANSLATE_ME)\b')
                self.assertTrue(value.strip())
    def test_subject_concepts_and_dynamic_names_resolve_to_english(self):
        def expand(key):
            return DOLLAR.sub(lambda m:expand(m[1]) if m[1] in self.en else m[0],self.en[key])
        for kind,label in [('trading_post','Trading Post'),('province','Province')]:
            for key in ('concept_crb_'+kind,'subject_type_crb_'+kind,'subject_type_crb_'+kind+'_no_icon','crb_'+kind):
                with self.subTest(key=key):self.assertEqual(expand(key),label)
            self.assertNotIn('@',self.en['concept_crb_'+kind])
        for target,region in [('lixus','FEZ'),('kerne','WEST_SAHARA'),('chretes','SENEGAL'),('chariot','SOUTH_CAMEROON')]:
            key='crb_hv_'+target+'_tt';name=self.en['STATE_'+region+'_crb']
            self.assertIn('$STATE_'+region+'_crb$',self.en[key]);self.assertIn(name,expand(key))
        self.assertEqual(self.en['crb_ordinal_4'],'Fourth')
        self.assertEqual(self.en['crb_ordinal_12'],'Twelfth')
        self.assertEqual(self.en['crb_ordinal_many'],'Another')

if __name__=='__main__':unittest.main()
