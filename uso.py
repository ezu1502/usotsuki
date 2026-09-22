from usotsuki.core import Game
from usotsuki.ui import UsoWindow


if __name__ == "__main__":
    usotsuki = Game()

    window = UsoWindow(game = usotsuki)
    window.run()


# *FEITO corrigir bug no trick
# *FEITO implementar placar da rodada
# *FEITO implementar placar geral
# TODO implementar tela de vitória ou derrota
# TODO implementar menu inicial
# TODO implementar animação de cartas
# TODO melhorar lógica dos bots