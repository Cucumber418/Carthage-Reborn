"""Check company database references against vanilla's building rename list."""
import json
from pathlib import Path
import unittest

from test_territories import Node, parse

ROOT = Path(__file__).resolve().parents[1]


def identifiers(value):
    if isinstance(value, Node):
        yield value.key
        yield from identifiers(value.value)
    elif isinstance(value, list):
        for item in value:
            yield from identifiers(item)
    elif isinstance(value, str):
        yield value


class CompanyBuildingIdentifierTests(unittest.TestCase):
    def test_company_definitions_do_not_use_obsolete_building_identifiers(self):
        fixture = json.loads((ROOT / 'tests/fixtures/renamed_buildings_1_12.json').read_text())
        paths = sorted((ROOT / 'common/company_types').glob('*.txt'))
        self.assertTrue(paths)
        for path in paths:
            tokens = set(identifiers(parse(path.read_text(encoding='utf-8-sig'))))
            obsolete = {old: new for old, new in fixture['renames'].items() if old in tokens}
            with self.subTest(file=path.relative_to(ROOT).as_posix()):
                self.assertFalse(obsolete, f'Use current building IDs; save aliases do not apply here: {obsolete}')
