"""Approved territory fixtures and discovery helpers shared by regressions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EUROPE = json.loads((ROOT / 'tests/fixtures/europe_regions.json').read_text())['regions']
TOTAL_REGIONS = 12 + len(EUROPE)
EXPECTED_EVENTS = 75 + len(EUROPE)
NATIVE_EVENT_COMPAT = json.loads((ROOT / 'tests/fixtures/vanilla_independence_events_1_15.json').read_text())


def native_event_localization_keys(path, key):
    """Only the two unchanged native events in the pinned compatibility file are external."""
    if key not in NATIVE_EVENT_COMPAT['events']:
        return None
    if path != NATIVE_EVENT_COMPAT['path']:
        raise AssertionError('Native compatibility event defined in an unexpected file: ' + path)
    return set(NATIVE_EVENT_COMPAT['events'][key])


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
