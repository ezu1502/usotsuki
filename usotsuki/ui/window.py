from __future__ import annotations
import arcade
from pathlib import Path
from arcade.types import Color
from usotsuki.toolbox import TimeCounter
from usotsuki.ui.view import PlayerView, CardView, TableView, ScoreView
import random
from typing_extensions import TYPE_CHECKING
from usotsuki.core.core import Bot

if TYPE_CHECKING:
    from usotsuki.core import Game, Player

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

        self.load_assets()

        self.bot_delay: float = self.set_bot_delay()

        self.match = self.game.match()

        self.current_player = next(self.match)
        self.make_visual_objects()
        
    def set_bot_delay(self) -> float:
        return random.uniform(0.7, 1.5)
    
    def play_or_advance(self):
        if not hasattr(self, "match"):
            self.match = self.game.match()
            self.current_player = next(self.match)

        if isinstance(self.current_player, Bot):
            self.current_player = self.match.send(self.current_player.choose())

        if hasattr(self, "players_view"):
            self.update_views()
            
        

    def run(self):
        arcade.run()

    # @TimeCounter
    def load_assets(self):
        
        self.font_path = Path(__file__).parent / "fonts" / "Sora-Regular.ttf"
        arcade.load_font(self.font_path)

        self.card_cache = {}
        for card in self.game.deck:
            self.card_cache[card] = arcade.load_texture(card.asset_path)

        self.card_cache["back"] = arcade.load_texture(Path(__file__).parent/"sprites"/"png"/"cards"/"card_back.png")

    # @TimeCounter
    def make_visual_objects(self):
        self.bg = arcade.LBWH(0, 0, *self.dimensions)

        self.table = arcade.SpriteList()
        
        table = arcade.Sprite(
            Path(__file__).parent.parent / "ui" / "sprites" / "png" / "table.png",
            center_x = self.center_x,
            center_y = self.center_y,
            scale = 0.5
        )
        self.table.append(table)
    
        self.pfps = arcade.SpriteList()

        self.table_view = TableView(self.game.vira, self.game.trick, self.card_cache, self.centered())
        

        self.players_view: list[PlayerView] = []
        for coordinate, player in zip(self.table_places(offset = 260), self.game.chair_order):
            player_view = PlayerView(player, self.card_cache, coordinate)
            self.players_view.append(player_view)

        self.this_player = self.players_view[0]

        self.score_view = ScoreView(self.game, self.dimensions)


    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.make_visual_objects()

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

    def get_text_obj(self, text: str, x: int, y: int, color: str = "#EEEEEE", size: int = 25):
        return arcade.Text(
            text = text,
            x = x,
            y = y,
            color = hex_color(color),
            font_size = size,
            anchor_x = "center",
            anchor_y = "center"
        )

    def centered(self, W: int = 0, H: int = 0) -> tuple[int, int]:
        x = (self.width - W) // 2
        y = (self.height - H) // 2
        return (x, y)

    def table_places(self, offset: int) -> list:
        """ Bottom, Left, Top, Right
        """

        x, y = self.center_coordinates

        return [
            (x, y - offset),
            (x - int(offset * 1.5), y),
            (x, y + offset),
            (x + int(offset * 1.5), y),
        ]

    @property
    def center_coordinates(self):
        return (int(self.width // 2), int(self.height // 2))
    
    #endregion
    #region Settings

    def update_views(self):
        for player in self.players_view:
            player.update_card_view()

        self.table_view.update()

    def on_key_press(self, key: int, modifiers: int):
        match key:
            case arcade.key.F11:
                self.set_fullscreen(not self.fullscreen)
            case arcade.key.R:
                if self.current_player == self.this_player.player:
                    print("truco")

    def on_draw(self):
        self.clear()

        arcade.draw_rect_filled(rect = self.bg, color = hex_color("#0E1020"))
        self.table.draw()
        
        self.table_view.draw()

        for p in self.players_view:
            p.draw()

        self.score_view.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.current_player != self.this_player.player: return

        cards = arcade.get_sprites_at_point((x, y), self.this_player.cards)
        if not cards: return

        card = cards[-1]

        self.current_player = self.match.send(card.card)
        self.bot_delay = self.set_bot_delay()
        self.update_views()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        cards = self.this_player.cards

        hovered_card = None

        for card in reversed(cards):
            if card.collides_with_point((x,y)):
                hovered_card = card
                break

        for card in cards:
            card.set_hover(card is hovered_card)

    def on_update(self, delta_time: float):
        if not isinstance(self.current_player, Bot):
            return
    
        self.bot_delay -= delta_time

        if self.bot_delay <= 0:
            self.play_or_advance()
            # self.bot_delay = self.set_bot_delay()

            if isinstance(self.current_player, Bot):
                self.bot_delay = self.set_bot_delay()

    #endregion



