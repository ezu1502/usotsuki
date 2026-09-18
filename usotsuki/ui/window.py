from __future__ import annotations
import arcade
from arcade.types import Color

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from usotsuki.core import Game

def hex_color(hex_string: str) -> Color:
    try:
        return Color.from_hex_string(hex_string)
    except ValueError:
        return Color(0, 0, 0)

#region INIT
class UsoWindow(arcade.Window):
    def  __init__(self, game: Game) -> None:
        self.game = game

        super().__init__(1280, 720, "Usotsuki", visible = False)
        self.maximize()
        self.set_visible(True)

    def run(self):
        arcade.run()

    #endregion
    #region Helpers
    @property
    def dimensions(self):
        return (self.width, self.height)

    def render_rect(self, L: int, B: int, W: int, H: int, rect_color: str = "#000000"):
        c = hex_color(rect_color)
        arcade.draw_rect_filled(
            rect = arcade.LBWH(L, B, W, H),
            color = c
        )

    def render_text(self, text: str, x: int, y: int, color: str = "#EEEEEE", size: int = 25):
        arcade.draw_text(
            text = text,
            x = x,
            y = y,
            color = hex_color("#EEEEEE"),
            font_size = size,
            anchor_x = "center",
            anchor_y = "center"
        )

    def centered(self, W: int, H: int) -> tuple[int, int]:
        x = (self.width - W) // 2
        y = (self.height - H) // 2
        return (x, y)

    def table_places(self, offset: int) -> list:
        """ Bottom, Left, Top, Right
        """

        x, y = self.center_coordinates

        return [
            (x, y - offset),
            (x - offset, y),
            (x, y + offset),
            (x + offset, y),
        ]

    @property
    def center_coordinates(self):
        return (int(self.center_x), int(self.center_y))
    
    #endregion
    #region Settings

    def on_key_press(self, key: int, modifiers: int):
        match key:
            case arcade.key.F11:
                self.set_fullscreen(not self.fullscreen)

    def on_draw(self):
        self.clear()

        self.render_rect(0, 0, *self.dimensions, "#0F4D4D")

        self.render_rect(*self.centered(200, 200), 200, 200, "#88C7C7")

        for coordinate, player in zip(self.table_places(offset = 170), self.game.chair_order):
            self.render_text(f"{player.name}", *coordinate)

    #endregion



