from __future__ import annotations
import arcade
from pathlib import Path
from arcade.types import Color
from usotsuki.toolbox import TimeCounter
from usotsuki.ui.view import PlayerView, CardView, TableView, ScoreView
import random
from typing_extensions import TYPE_CHECKING
from usotsuki.core.core import Bot
from usotsuki.core.enums import Teams, GameState as GS, Actions
from  usotsuki.core import Game

if TYPE_CHECKING:
    from usotsuki.core import Player

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

        self.state: GS = GS.MENU
       
        self.maximize()
        self.set_visible(True)

        self.load_assets()

        self.winner_screen_text = self.get_text_obj("", *self.centered())
        self.winner_screen_time = 0.0
                

        self.bot_delay: float = self.set_bot_delay()

        self.match = self.game.match()

        
        self.advance_match()
        self.make_visual_objects()
        self.trucando = False

    def start(self):
        
        self.set_state(GS.PLAYING)

    def restart(self):
        self.game = Game()
        self.match = self.game.match()
        self.bot_delay = self.set_bot_delay()
        self.advance_match()
        self.make_visual_objects()

    def set_bot_delay(self) -> float:
        return random.uniform(0.7, 1.5)

    def set_state(self, state: GS) -> None:
        self.state = state
    
    def match_finished(self, team):
        self.winner_screen_text.text = f"MATCH FINISHED! The winner is {team.value.capitalize()}"
        self.set_state(GS.MATCH_END)

    def round_finished(self, result):
        self.winner_screen_time = 1.0
        self.winner_screen_text.text = f"{result.value.capitalize()} won the round!"
        self.set_state(GS.ROUND_END)

    def advance_match(self, value = None):
        try:
            if value is None:
                result = next(self.match)
            else:
                result = self.match.send(value)

        except StopIteration as e:
            self.match_finished(e.value)   
            return

        if isinstance(result, Teams):
            self.round_finished(result)
            self.advance_match()
            return

        self.current_player = result

    def play_or_advance(self):
        if isinstance(self.current_player, Bot):
            if self.trucando:
                response = self.current_player.choose(options = [Actions.ACCEPT, Actions.RAISE, Actions.FOLD])
            else:    
                response = self.current_player.choose()
            

            self.advance_match(response)

            if response == Actions.RAISE:
                self.trucando = True
                self.truco_text.text = self.game.truco_string()
            else:
                self.trucando = False


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

        self.truco_text = self.get_text_obj(
            "",
            *self.centered(),
            color = "#FF0000",
            size = 60
        )

        self.truco_rect = arcade.LBWH(0, 0, self.width, self.height)

        self.title = self.get_text_obj(
            "Usotsuki - Brazilian Truco",
            self.width // 2,
            self.height // 2,
            color = "#EEEEEE",
            size = 50
        )

        self.subtitle = self.get_text_obj(
            "- press any key to continue -",
            self.width // 2,
            self.height // 2 - 50,
            color = "#EEEEEE",
            size = 20
        )


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
            font_name = "Sora",
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
        if self.state == GS.MATCH_END:
            self.set_state(GS.PLAYING)

            self.restart()

            return

        if self.state == GS.MENU:
            self.start()

        
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        if key == arcade.key.ESCAPE:
            self.set_fullscreen(False)

        if self.current_player == self.this_player.player:
            match key:
                case arcade.key.R:
                    self.bot_delay = self.set_bot_delay()
                    self.advance_match(Actions.RAISE)

                    self.trucando = True
                    self.truco_text.text = self.game.truco_string()
                case arcade.key.F:
                    self.trucando = False
                    self.advance_match(Actions.FOLD)
                case arcade.key.A:
                    if self.trucando:
                        self.advance_match(Actions.ACCEPT)

    def on_draw(self):
        self.clear()

        if self.state == GS.ROUND_END:
            self.winner_screen_text.draw()
            return
        if self.state == GS.MATCH_END:
            self.winner_screen_text.draw()
            return
        if self.state == GS.MENU:
            arcade.draw_rect_filled(rect = self.bg, color = hex_color("#113025"))
            self.title.draw()
            self.subtitle.draw()
            return
        
        arcade.draw_rect_filled(rect = self.bg, color = hex_color("#0E1020"))
        self.table.draw()
        
        self.table_view.draw()

        for p in self.players_view:
            p.draw()

        self.score_view.draw()

        if self.trucando:
            self.truco_text.draw()

        if self.game.current_value > 1:
            arcade.draw_rect_outline(rect = self.truco_rect, color = Color(255, 0, 0), border_width = 10)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.current_player != self.this_player.player: return

        cards = arcade.get_sprites_at_point((x, y), self.this_player.cards)
        if not cards: return

        card = cards[-1]

        self.advance_match(card.card)
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
        if self.state == GS.ROUND_END:
            self.winner_screen_time -= delta_time

            if self.winner_screen_time <= 0:
                self.set_state(GS.PLAYING)
                self.advance_match()

            return

        if self.state == GS.MATCH_END:
            return

        if self.state == GS.MENU:
            return

        if not isinstance(self.current_player, Bot):
            return
    
        self.bot_delay -= delta_time

        if self.bot_delay <= 0:
            self.play_or_advance()
            # self.bot_delay = self.set_bot_delay()

            if isinstance(self.current_player, Bot):
                self.bot_delay = self.set_bot_delay()

    #endregion



