from __future__ import annotations
import arcade
import random
from usotsuki.toolbox import TimeCounter

from typing_extensions import TYPE_CHECKING
if TYPE_CHECKING:
    from usotsuki.core import Card, Player

class TableView:
    def __init__(self, vira, trick, cache: dict) -> None:
        self.cache = cache


        self.vira = vira if vira else None
        self.trick: list[Card] = trick if trick else []

        self.cards = arcade.SpriteList()

        self.update()

    def update(self):
        self.cards.clear()

        for card in self.trick:
            c = CardView(card, texture = self.cache[card])
            c.angle = random.randint(-90, 90)
            self.cards.append(c)

        if self.vira:
            vira_view = CardView(self.vira, self.cache[self.vira])
            self.back = CardView(None, texture = self.cache["back"])
            self.back.set_angle(70)

            self.cards.append(vira_view)
            self.cards.append(self.back)

    def draw(self):
        self.cards.draw()

    def set_position(self, x, y):
        self.x = x
        self.y = y

        for c in [v for v in self.cards if v != self.back]:
            card: arcade.Sprite = c

            card.center_x = x
            card.center_y = y

        self.back.center_x = x
        self.back.center_y = y - 30


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
    def __init__(self, player: Player, texture_cache: dict) -> None:
        self.player = player
        self.cache = texture_cache

        self.pfp_list = arcade.SpriteList()
        self.pfp = arcade.Sprite(self.player.pfp, scale = 0.4)
        self.pfp_list.append(self.pfp)

        

        self.cards = arcade.SpriteList()
        self.update_card_view()

    def update_card_view(self):
        self.cards.clear()
        for card in self.player.cards:
            card_view = CardView(card = card, texture = self.cache[card])
            self.cards.append(card_view)

    def set_position(self, x, y):
        self.x = x
        self.y = y

        self.pfp.center_x = x
        self.pfp.center_y = y + 40

        for i, c in enumerate(self.cards, start = -1):
            card: CardView = c

            card.set_position(x + i * 20, y - 40)

            card.angle = 20*i

    def draw(self):
        self.pfp_list.draw()
        self.cards.draw()