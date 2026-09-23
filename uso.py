from usotsuki.core import Game
from usotsuki.ui import UsoWindow


if __name__ == "__main__":
    usotsuki = Game()

    window = UsoWindow(game = usotsuki)
    window.run()


# *FEITO corrigir bug no trick
# *FEITO implementar placar da rodada
# *FEITO implementar placar geral
# *FEITO implementar tela de vitória ou derrota
# *FEITO adaptar a lógica do truco pro generator
# *FEITO implementar representação visual de truco 
# *FEITO implementar menu inicial
# PARA A v0.2 melhorar lógica dos bots