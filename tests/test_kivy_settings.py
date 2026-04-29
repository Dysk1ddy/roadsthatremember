from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace
import unittest
import uuid

from dnd_game.content import build_character, create_elira_dawnmantle, create_tolan_ironshield
from dnd_game.game import TextDnDGame
from dnd_game.models import GameState

try:
    from dnd_game.gui import (
        ClickableTextDnDGame,
        GameScreen,
        KIVY_SIDE_COMMAND_CLOSE_TOKEN,
        KivySideCommandClosed,
        NativeCommandWorkspace,
    )
except Exception as exc:  # pragma: no cover - depends on optional Kivy runtime
    ClickableTextDnDGame = None
    GameScreen = None
    KIVY_SIDE_COMMAND_CLOSE_TOKEN = ""
    KivySideCommandClosed = Exception
    NativeCommandWorkspace = None
    KIVY_IMPORT_ERROR = exc
else:
    KIVY_IMPORT_ERROR = None


class FakeKivyBridge:
    def __init__(self) -> None:
        self.screen = SimpleNamespace(kivy_dark_mode_enabled=True, kivy_fullscreen_enabled=False)
        self.outputs: list[str] = []
        self.choice_responses: list[str] = []
        self.choice_prompts: list[tuple[str, list[str]]] = []
        self.side_command_active = False
        self.native_commands: list[str] = []

    def post_output(self, text: object = "") -> None:
        self.outputs.append(str(text))

    def request_choice(
        self,
        prompt: str,
        options: list[str],
        *,
        option_details: dict[str, str] | None = None,
    ) -> str:
        del option_details
        self.choice_prompts.append((prompt, list(options)))
        return self.choice_responses.pop(0) if self.choice_responses else "1"

    def set_kivy_dark_mode(self, enabled: bool) -> None:
        self.screen.kivy_dark_mode_enabled = bool(enabled)

    def set_kivy_fullscreen(self, enabled: bool) -> None:
        self.screen.kivy_fullscreen_enabled = bool(enabled)

    def show_native_command(self, command: str) -> None:
        self.native_commands.append(command)


@unittest.skipIf(ClickableTextDnDGame is None, f"Kivy unavailable: {KIVY_IMPORT_ERROR}")
class KivySettingsTests(unittest.TestCase):
    def make_save_dir(self) -> Path:
        save_dir = Path.cwd() / "tests_output" / f"kivy_settings_{uuid.uuid4().hex}"
        save_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(save_dir, ignore_errors=True))
        return save_dir

    def test_fullscreen_setting_loads_applies_and_persists(self) -> None:
        save_dir = self.make_save_dir()
        settings_path = save_dir / "settings.json"
        settings_path.write_text(
            json.dumps(
                {
                    "kivy_dark_mode_enabled": False,
                    "kivy_fullscreen_enabled": True,
                }
            ),
            encoding="utf-8",
        )
        bridge = FakeKivyBridge()

        game = ClickableTextDnDGame(bridge, save_dir=save_dir)

        self.assertTrue(game.current_settings_payload()["kivy_fullscreen_enabled"])
        self.assertTrue(bridge.screen.kivy_fullscreen_enabled)
        self.assertFalse(game.current_settings_payload()["kivy_dark_mode_enabled"])

        game.set_kivy_fullscreen_enabled(False)

        stored_settings = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertFalse(stored_settings["kivy_fullscreen_enabled"])
        self.assertFalse(bridge.screen.kivy_fullscreen_enabled)

    def test_story_choice_reopens_after_unexpected_side_close_token(self) -> None:
        save_dir = self.make_save_dir()
        bridge = FakeKivyBridge()
        bridge.choice_responses = [KIVY_SIDE_COMMAND_CLOSE_TOKEN, "2"]
        game = ClickableTextDnDGame(bridge, save_dir=save_dir)

        choice = game.choose_with_display_mode("Choose a path.", ["First", "Second"], allow_meta=False)

        self.assertEqual(choice, 2)
        self.assertEqual([prompt for prompt, _options in bridge.choice_prompts], ["Choose a path.", "Choose a path."])

    def test_active_side_command_choice_close_still_cancels_side_command(self) -> None:
        save_dir = self.make_save_dir()
        bridge = FakeKivyBridge()
        bridge.side_command_active = True
        bridge.choice_responses = [KIVY_SIDE_COMMAND_CLOSE_TOKEN]
        game = ClickableTextDnDGame(bridge, save_dir=save_dir)

        with self.assertRaises(KivySideCommandClosed):
            game.choose_with_display_mode("Manage inventory.", ["View inventory"], allow_meta=False)

    def test_out_of_combat_journal_inventory_and_gear_use_native_command_panes(self) -> None:
        save_dir = self.make_save_dir()
        bridge = FakeKivyBridge()
        game = ClickableTextDnDGame(bridge, save_dir=save_dir)
        player = build_character(
            name="Vale",
            race="Human",
            class_name="Warrior",
            background="Soldier",
            base_ability_scores={"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
            class_skill_choices=["Athletics", "Survival"],
        )
        game.state = GameState(player=player)

        self.assertTrue(game.handle_meta_command("journal"))
        self.assertTrue(game.handle_meta_command("inventory"))
        self.assertTrue(game.handle_meta_command("gear"))
        self.assertTrue(game.handle_meta_command("camp"))

        self.assertEqual(bridge.native_commands, ["journal", "inventory", "gear", "camp"])

    def make_command_screen(self, *, state=None, in_combat: bool = False):
        screen = GameScreen.__new__(GameScreen)
        game = SimpleNamespace(state=state, _in_combat=in_combat)
        screen.active_game = lambda: game
        screen.combat_active = lambda: in_combat
        screen.kivy_dark_mode_enabled = True
        return screen

    def test_command_bar_keeps_unavailable_commands_visible(self) -> None:
        screen = self.make_command_screen(state=None)

        self.assertEqual(screen._command_bar_commands_for_context(), tuple(GameScreen.COMMANDS))

    def test_command_bar_explains_combat_unavailable_commands(self) -> None:
        state = SimpleNamespace(player=object())
        screen = self.make_command_screen(state=state, in_combat=True)

        self.assertEqual(screen._command_unavailable_reason("map"), "Maps are unavailable during combat.")
        self.assertEqual(
            screen._command_unavailable_reason("gear"),
            "You cannot reorganize equipment in the middle of combat.",
        )
        self.assertEqual(screen._command_unavailable_reason("camp"), "You cannot head to camp during combat.")
        self.assertEqual(screen._command_unavailable_reason("journal"), "")

    def test_unavailable_command_button_prints_reason_instead_of_submitting(self) -> None:
        screen = self.make_command_screen(state=SimpleNamespace(player=object()), in_combat=True)
        hidden: list[tuple[bool, bool]] = []
        messages: list[str] = []
        submitted: list[str] = []
        screen._set_command_bar_visible = lambda visible, *, animate: hidden.append((visible, animate))
        screen.post_command_unavailable_message = messages.append
        screen.submit_direct = submitted.append

        screen.submit_command("map")

        self.assertEqual(hidden, [(False, True)])
        self.assertEqual(messages, ["Maps are unavailable during combat."])
        self.assertEqual(submitted, [])

    def make_native_command_game(self) -> TextDnDGame:
        player = build_character(
            name="Vale",
            race="Human",
            class_name="Warrior",
            background="Soldier",
            base_ability_scores={"STR": 15, "DEX": 14, "CON": 13, "INT": 8, "WIS": 12, "CHA": 10},
            class_skill_choices=["Athletics", "Survival"],
        )
        game = TextDnDGame(input_fn=lambda _: "1", output_fn=lambda _: None)
        game.state = GameState(
            player=player,
            companions=[create_tolan_ironshield()],
            camp_companions=[create_elira_dawnmantle()],
            current_scene="iron_hollow_hub",
            gold=125,
            inventory={
                "potion_healing": 1,
                "travel_biscuits": 3,
                "longsword_common": 1,
                "iron_cap_common": 1,
            },
        )
        game.add_journal("The road ledger keeps Vale's promise in black ink.")
        game.add_clue("A chalk mark dries on the wagon board.")
        game.ensure_state_integrity()
        return game

    def test_native_command_workspace_renders_panes_refreshes_camp_and_goes_back(self) -> None:
        assert NativeCommandWorkspace is not None
        game = self.make_native_command_game()
        closed: list[bool] = []
        screen = SimpleNamespace(
            theme=GameScreen.DARK_THEME,
            width=480,
            active_game=lambda: game,
            close_side_command_panel=lambda: closed.append(True),
            _apply_font=lambda _widget, _role: None,
            side_command_title_label=SimpleNamespace(text=""),
        )
        workspace = NativeCommandWorkspace(screen)
        workspace.width = 480

        workspace.render_command("journal")
        self.assertEqual(workspace.mode, "journal")
        workspace.render_inventory(filter_key="consumables")
        self.assertEqual(workspace.inventory_filter_key, "consumables")
        workspace.render_gear(selected_slot="head")
        self.assertEqual(workspace.gear_selected_slot, "head")
        workspace.render_camp(view="recovery")
        self.assertEqual(workspace.camp_view, "recovery")

        workspace.refresh_active()
        self.assertEqual(workspace.mode, "camp")
        self.assertEqual(workspace.camp_view, "recovery")

        workspace.go_back()
        self.assertEqual(workspace.camp_view, "overview")
        workspace.go_back()
        self.assertEqual(closed, [True])


if __name__ == "__main__":
    unittest.main()
