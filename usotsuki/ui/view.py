from __future__ import annotations
import arcade
import random
from pathlib import Path
from usotsuki.core import Bot

from usotsuki.toolbox import TimeCounter

from typing_extensions import TYPE_CHECKING
if TYPE_CHECKING:
    from usotsuki.core import Card, Player, Game

class TableView:
    def __init__(self, vira, trick, cache: dict, coordinate: tuple[int, int]) -> None:
        self.x, self.y = coordinate
        self.cache = cache

        self.vira = vira
        self.trick: list[Card] = trick

        self.vira_view = None
        self.trick_view = arcade.SpriteList()

        self.cards = arcade.SpriteList()
        self.back_view = arcade.SpriteList()


        self.back = CardView(None, texture = self.cache["back"])
        self.back.set_angle(70)
        self.back_view.append(self.back)
        
        self.update()

    def update(self):
    
        if self.vira and self.vira_view is None:
            self.vira_view = CardView(self.vira, self.cache[self.vira])
            self.cards.append(self.vira_view)

        

        for card in self.trick:
            if card not in [view.card for view in self.trick_view]:
                c = CardView(card, texture = self.cache[card])
                c.angle = random.randint(-90, 90)
                self.trick_view.append(c)

        for view in list(self.trick_view):
            if view.card not in self.trick:
                self.trick_view.remove(view)

        self.set_position(self.x, self.y)

    def draw(self):
        self.cards.draw()
        self.trick_view.draw()
        self.back_view.draw()

    def set_position(self, x, y):
        self.x = x
        self.y = y

        for view in self.trick_view:
            view.center_x, view.center_y = self.x, self.y

        if self.vira_view:
            self.vira_view.center_x, self.vira_view.center_y = self.x + 110, self.y + 110

        self.back.center_x, self.back.center_y = self.x + 110, self.y + 90


class CardView(arcade.Sprite):
    def __init__(self, card: Card | None, texture) -> None:

        

        super().__init__(texture, scale = 0.13)
        self.card = card

        self.x = self.center_x
        self.y = self.center_y

    def set_position(self, x: int, y: int, angle: int = 0):
        self.x = x
        self.y = y

        self.center_x = x
        self.center_y = y

        self.angle = angle

    def set_angle(self, angle):
        self.angle = angle

    def set_hover(self, hover: bool):
        if hover:
            self.center_y = self.y + 15

        else:
            self.center_y = self.y


    def __str__(self) -> str:
        return f"View: {self.card}"

class PlayerView:
    def __init__(self, player: Player, texture_cache: dict, coordinate: tuple[float, float]) -> None:
        self.x, self.y = coordinate

        self.player = player
        self.cache = texture_cache

        self.pfp_list = arcade.SpriteList()
        self.pfp = arcade.Sprite(self.player.pfp, scale = 0.4)
        self.pfp_list.append(self.pfp)

        self.name_text = arcade.Text (
            self.player.name,
            self.x,
            self.y + 100,
            color = arcade.color.WHITE,
            font_name = "Sora",
            font_size = 18,
            anchor_x = "center",
            anchor_y = "center"
        )

        self.cards = arcade.SpriteList()
        self.update_card_view()

    def update_card_view(self):
        player_cards = set(self.player.cards)
        view_cards = {view.card: view for view in self.cards}

        for card, view in view_cards.items():
            if card not in player_cards:
                self.cards.remove(view)

        for card in self.player.cards:
            if card not in view_cards:
                texture = self.cache[card] if not isinstance(self.player, Bot) else self.cache["back"]
                self.cards.append(CardView(card, texture))

        
        self.set_position(self.x, self.y)

    def set_position(self, x, y):
        self.x = x
        self.y = y

        self.pfp.center_x = x
        self.pfp.center_y = y + 40

        for i, c in enumerate(self.cards, start = -1):
            card: CardView = c

            card.set_position(x + i * 20, y - 40)

            card.angle = 20*i

        self.name_text.x = self.x 
        self.name_text.y = self.y + 100

    def draw(self):
        self.pfp_list.draw()
        self.cards.draw()
        self.name_text.draw()

class ScoreView:
    def __init__(self, game, dimensions: tuple) -> None:
        self.game: Game = game
        self.width, self.height = dimensions

        self.score_text = arcade.Text(
            "",
            self.width - 100,
            20,
            arcade.color.WHITE,
            font_size = 30,
            font_name = "Sora"
        )

    @property
    def score(self):
        return self.game.score_odd, self.game.score_even

    @property
    def round_score(self):
        return self.game.round_score_odd, self.game.round_score_even
    
    def draw(self):
        for i in range(self.round_score[0]):
            arcade.draw_circle_filled(40 + 55*i, self.height - 40, 15, arcade.color.WHITE)

        for i in range(self.round_score[1]):
            arcade.draw_circle_filled(self.width - 40 - 55*i, self.height - 40, 15, arcade.color.WHITE)

        self.score_text.text = f"{self.score[0]}x{self.score[1]}"
        self.score_text.draw()


        
        


        
