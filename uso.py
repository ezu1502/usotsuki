from usotsuki.core import Game
from usotsuki.ui import UsoWindow


if __name__ == "__main__":
    usotsuki = Game()

    window = UsoWindow(game = usotsuki)
    window.run()