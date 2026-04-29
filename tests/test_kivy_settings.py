from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace
import unittest
import uuid

try:
    from dnd_game.gui import ClickableTextDnDGame, GameScreen, KIVY_SIDE_COMMAND_CLOSE_TOKEN, KivySideCommandClosed
except Exception as exc:  # pragma: no cover - depends on optional Kivy runtime
    ClickableTextDnDGame = None
    GameScreen = None
    KIVY_SIDE_COMMAND_CLOSE_TOKEN = ""
    KivySideCommandClosed = Exception
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


if __name__ == "__main__":
    unittest.main()
