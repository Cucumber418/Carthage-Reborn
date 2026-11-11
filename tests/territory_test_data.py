"""Approved territory fixtures and discovery helpers shared by regressions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EUROPE = json.loads((ROOT / 'tests/fixtures/europe_regions.json').read_text())['regions']
TOTAL_REGIONS = 12 + len(EUROPE)
EXPECTED_EVENTS = 74 + len(EUROPE)


def buttons(scripts, prefix):
    from test_territories import Node
    return [node for path, nodes in scripts.items()
            if path.startswith('common/scripted_buttons/')
            for node in nodes if isinstance(node, Node)
            and node.key.startswith(prefix) and node.key.endswith('_button')]


def formation_buttons(scripts):
    from test_territories import Node
    return buttons(scripts, 'crb_found_') + [node for path, nodes in scripts.items()
            if path.startswith('common/scripted_buttons/')
            for node in nodes if isinstance(node, Node) and node.key == 'crb_handle_rome_button']
