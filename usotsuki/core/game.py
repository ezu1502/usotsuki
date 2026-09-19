from usotsuki.core import Ranks, Suits, Card, Deck, Player, Bot
import random
from pathlib import Path

def clip(number: int, mini: int, maxi: int) -> int:
    return maxi if number > maxi else mini if number < mini else number

sprites_folder: Path = Path(__file__).parent.parent / "ui" / "sprites" / "png"

class Game:
    def __init__(self) -> None:
        self.pfps = ["ado.png", "bolsonaro.png", "cr7.png", "dio.png"]

        self.players: list[Player] = self.summon_players()

        self.chair_order: list[Player] = self.players.copy()

        self.deck = Deck()

        self.team_odd, self.team_even = self.get_teams()

        self.score_odd, self.score_even = 0, 0
        self.round_score_odd, self.round_score_even = 0, 0

        self.vira: Card | None = None

        self.trick: list[Card] = []
        self.pile: list[Card] = []

        self.current_value: int = 1

    @property
    def manilha(self):
        if self.vira is None:
            return None
        
        return Ranks((self.vira.rank + 1) % len(Ranks))

    def summon_players(self) -> list[Player]:
        names = ["Ado", "Bolsonaro", "Cristiano Ronaldo", "Dio"]
        return [Player(sprites_folder / self.pfps[0], names[0])] + [Bot(sprites_folder / pfp, name) for pfp, name in zip(self.pfps[1:], names[1:])]

    def get_teams(self) -> tuple[list[Player], list[Player]]:
        random.shuffle(self.players)

        return (self.players[::2], self.players[1::2])

    def receive_card(self, card: Card):
        if self.vira is not None:
            return

        self.vira = card

    def turn(self, player: Player):
        cards = [f"[{indx}] - {card}" for indx, card in enumerate(player.cards, start = 1)]

        trick = f"Cards in trick: {", ".join(map(str, self.trick))}" if self.trick else "- First to play -"

        raising = "call TRUCO" if self.current_value == 1 else f"call it {self.current_value + 3}"
        options = (
            f"VIRA: {self.vira}\n\n"
            f"{trick}\n\n"
            f"Your turn now, {player.name}!\n\n"
            f"Your cards are: \n{",\n".join(cards)}\n\n"
            f"Type the number of your card to play it, [R] to {raising} or [F] to FOLD!\n> "
        )
        j = 0
        while j < 3:
            choice = player.choose(options) if j == 0 else player.choose(f"{{{j}}} > ")

            if choice.upper() in ["1", "2", "3", "F", "R", "TRUCO"]:
                return choice
            j += 1

        return random.randint(1, len(player.cards))

    def card_strength(self, card: Card):
        if card.rank == self.manilha:
            return 100 + card.suit

        return card.rank

    def rotate_players(self, last_winner: Player) -> None:
        i: int = self.players.index(last_winner)
        self.players = self.players[i:] + self.players[:i]

    
    def finish_step(self, special = False) -> bool:
        best_cards = sorted(self.trick, key = self.card_strength, reverse = True)

        if best_cards[0].rank != self.manilha:
            if best_cards[0].rank == best_cards[1].rank:
                # ! MELOU
                return False

        winner_player = next(player for player in self.players if player.had(best_cards[0]))

        value = 3 if special else 1

        self.give_points(winner_player, value)

        print(f"{winner_player.name.upper()} WON THE STEP!")
        print(f"Hand Score: ODD {self.round_score_odd}-{self.round_score_even} EVEN")


        self.pile.extend(self.trick)
        self.trick.clear()

        self.rotate_players(winner_player)
        return True

    def truco(self, to_player):
        i = 0

        while i < 3:
            question = (
                "[A] - Accept\n"
                "[F] - Fold\n"
                f"[R] - Call it {min(self.current_value + 3, 12)}"
            ) 

            response = to_player.choose(question, options = ["a", "f", "r"]) if i == 0 else to_player.choose(f"{{{i}}} > ")

            if response.lower() in ["a", "f", "r"]:
                return response.lower()

            i += 1


        return "f"
            



    def give_points(self, player: Player, points: int):
        if player in self.team_odd:
            self.round_score_odd += points
        elif player in self.team_even:
            self.round_score_even += points

    def in_odd_team(self, player: Player) -> bool:
        return player in self.team_odd

    def match(self):

        # TODO Implementar lógica de pedir truco, foldar
        
        def distribute_cards():
            for player in self.players:
                player.reset()
                self.deck.give_card(player, 3)

            self.deck.give_card(self, 1)

        def step() -> bool:
            for i, player in enumerate(self.players):
                choice = self.turn(player)
                try:
                    choice = clip(int(choice) - 1, 0, len(player) - 1)
                    card: Card = player.cards.pop(choice)

                    self.trick.append(card)

                    print(f"\n -- {player.name} played the {card} --")

                except ValueError:
                    choice = str(choice)
                    match choice.lower():
                        case "f":
                            print(f"-- {player.name} folded! --")
                            if self.in_odd_team(player):
                                self.round_score_even += 3
                            else:
                                self.round_score_odd += 3

                            return True
                            
                        case "r" | "truco":
                            print(f"{player.name.upper()} called TRUCO!\n\n")


                            next_responding = True
                            p = self.players[(i+1) % len(self.players)] if next_responding else player

                            while True:
                                response = self.truco(p)

                                if response != "r":
                                    break

                                
                                print(f"{p.name.upper()} called it {self.current_value}!\n\n")

                                self.current_value = 3 if self.current_value == 1 else self.current_value + 3

                                next_responding = not next_responding
                                p = self.players[(i+1) % len(self.players)] if next_responding else player

                            match response:
                                case "a":
                                    print(f"{p.name} accepted!")
                                case "f":
                                    print(f"-- {p.name} folded! --")
                                    next_responding = not next_responding
                                    p = self.players[(i+1) % len(self.players)] if next_responding else player

                                    self.give_points(p, 3)
        
                                    return True

            theres_a_victor = self.finish_step()

            if not theres_a_victor:
                # ! MELOU
                def melou() -> bool:
                    if any(len(player) == 0 for player in self.players):

                        if self.round_score_odd > self.round_score_even:
                            self.round_score_odd = 3
                            return True
                        elif self.round_score_even > self.round_score_odd:
                            self.round_score_even = 3
                            return True


                        print("DRAW! No points were given")
                        return False
                    for player in self.players:
                        card = max(player.cards, key = self.card_strength)
                        player.cards.remove(card)

                        self.trick.append(card)

                    now_there_is_a_victor = self.finish_step(special = True)
                    if not now_there_is_a_victor:
                        return melou()

                    return True

                return melou()
                

            return True

        def round():
            self.round_score_even, self.round_score_odd = 0, 0
            self.trick.clear()
            self.pile.clear()
            self.deck.reset()

            self.vira = None
            self.current_value = 1

            distribute_cards()
            print("dddddddd")

            yield 1

            print("\n\n##  ROUND START!  ##\n\n")
            while self.round_score_odd < 2 and self.round_score_even < 2:
                st = step()
                if not st:
                    return
                
            if self.round_score_odd >= 2:
                self.score_odd += self.current_value
            elif self.round_score_even >= 2:
                self.score_even += self.current_value
            else:
                raise RuntimeError("Bro, idk what happened here")


        while self.score_even < 12 and self.score_odd < 12:
            r = round()
            next(r)
            yield 1


            
            