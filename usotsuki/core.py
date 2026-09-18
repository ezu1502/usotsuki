import random
from dataclasses import dataclass
from usotsuki import Ranks, Suits
from time import sleep

@dataclass(frozen = True)
class Card:
    rank: Ranks
    suit: Suits

    def __gt__(self, other):
        if isinstance(other, Card):
            return self.rank > other.rank
        
        return NotImplemented

    def __str__(self) -> str:
        suit = self.suit.name.lower().capitalize()
        rank = self.rank.name.lower().capitalize()


        return f"{rank} of {suit}"


class Deck:
    def __init__(self) -> None:
        self.cards: list[Card] = self.generate_cards()
        self.burned_cards: list[Card] = []

        self.shuffle()

    def reset(self):
        self.__init__()

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)
    
    def generate_cards(self) -> list[Card]:
        return [Card(suit = suit, rank = rank) for suit in Suits for rank in Ranks]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

    def give_card(self, target, amount: int):
        if not hasattr(target, "receive_card"):
            return

        for _ in range(amount):
            target.receive_card(self.draw())


class Player:
    def __init__(self, name: str = "player") -> None:
        self.cards: list[Card] = []
        self.cards_of_round: set[Card] = set(self.cards)
        self.name: str = name

    def receive_card(self, card):
        if len(self.cards) >= 3:
            raise RuntimeError("Player already has 3 cards!")

        self.cards.append(card)
        self.cards_of_round.add(card)

    def choose(self, question: str):
        return input(question)

    def had(self, card: Card) -> bool:
        return card in self.cards_of_round

    def reset(self):
        self.cards_of_round.clear()
        self.cards.clear()

    def __len__(self):
        return len(self.cards)
    
    def __iadd__(self, other):
        if isinstance(other, Card):
            self.cards.append(other)
        else:
            return NotImplemented

class Bot(Player):
    def __init__(self, name: str = "player") -> None:
        super().__init__(name)

    def choose(self, question: str):
        sleep(1)
        return str(random.randint(1, len(self.cards)))
    
    
