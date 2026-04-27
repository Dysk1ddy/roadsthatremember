# Magic Point System Notes

Last updated: 2026-04-27

The live class surface now uses three preset classes: Warrior, Mage, and Rogue. MP is a Mage-facing resource, with room for future feature-based channeling through explicit feature ids.

## Runtime Sources

- `dnd_game/gameplay/magic_points.py`
- `dnd_game/gameplay/spell_slots.py`
- `dnd_game/data/story/character_options/classes.py`
- `dnd_game/data/story/public_terms.py`
- `tests/test_core.py`

## Current Formula

| User type | Formula | Notes |
| --- | --- | --- |
| Mage | `6 + 4 * level + max(0, spellcasting modifier)` | Uses `INT` from the Mage class definition. |
| Feature channeler | `3 + max(0, spellcasting modifier)` | Reserved for future `magic_initiate` or `racial_magic` access. |
| Warrior / Rogue | none | No MP row unless a future feature grants access. |

MP is stored in `resources["mp"]`; maximum MP is stored in `max_resources["mp"]`. Reconciliation removes MP rows from characters that no longer qualify.

## Implemented Costs

| Channel | Cost | Action lane |
| --- | ---: | --- |
| Minor Channel | 1 | action |
| Arc Pulse | 1 | action |
| Marked Angle | 1 | bonus action |
| Ember Lance | 1 | action |
| Frost Shard | 1 | action |
| Volt Grasp | 1 | action |
| Burning Line | 4 | action |
| Lockfrost | 4 | action |
| Field Mend | 3 | action |
| Pulse Restore | 4 | bonus action |
| Triage Line | 3 | action |
| Clean Breath | 2 | action |
| Anchor Shell | 3 | bonus action |
| Ward Shell | 2 | reaction-style guard feature |
| Blue Glass Palm | 1 | action |
| Lockstep Field | 3 | action |

## Rest And Consumables

- Short rest restores half maximum MP, rounded up.
- Long rest restores all MP.
- MP-refresh items convert old charge-band restore units into MP at `4 MP` per unit.
- Charge-band data still synchronizes for compatibility, but combat menus and HUD surfaces speak in MP.

## Current Test Coverage

- MP summary and HUD bars
- Insufficient MP messaging
- Short-rest and long-rest restoration
- Mage channel spend behavior
- Save/resource reconciliation after the old class list was retired
